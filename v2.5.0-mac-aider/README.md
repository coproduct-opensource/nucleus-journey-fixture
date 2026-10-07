# v2.5.0, Mac Apple-container host, aider

| | |
|---|---|
| Release | [v2.5.0](https://github.com/coproduct-opensource/nucleus/releases/tag/v2.5.0) |
| Node | aarch64 development microVM host in Apple `container` on the operator's Mac (`development: true`, no TPM) |
| Harness | aider 0.86.2, in a Firecracker pod (`c076fb32-2ed1-4f3a-ae15-8b49ade976b6`) |
| Run | 2026-10-06T18:41:10Z to 18:42:11Z (harness start and end, from `logs/stdout.bin`) |
| Result | https://github.com/coproduct-opensource/nucleus-journey-fixture/pull/1 (a fixture repository; its PRs stay open and are never merged) |
| Platform tier | **Unattested** (`no TPM attester configured (--node-evidence-tpm is unset)`) |
| AK anchor | none |
| Verifier | `nucleus-audit` 2.5.0, `aarch64-apple-darwin` |

A coding agent repaired `summary.py` in the fixture repository. The pod held no forge
credential. The push and the pull request went out through host-performed egress, and the
host held each one until the owner approved it (`approvals/APPROVAL_ATTRIBUTION.txt`). On v2.5.0 a pending approval lives 300 s. The
first two push requests expired before they were answered, and the third was granted
(`approvals/events.jsonl`).

## What the verdict says, and what it rests on

`verify-execution` returns `authorized_platform_not_attested`, with the platform tier
`unattested`, `from: receipt`. The signed receipt itself records that the node had no TPM
evidence. Evidence supplied beside a receipt can never upgrade that, so `--require-attested`
refuses it. This run makes **no claim about the node's boot or its binaries**. Secure Boot,
EFI applications, boot files and the kernel command line are not checked, and neither is
anything else about the host.

What the checks do establish:

- the receipt is signed by the executor key below, and agrees with the admission and the
  environment inputs: program digest, pod spec digest, exit code, and stdout/stderr digests;
- the artifact bundles and console logs are the bytes the receipt names;
- the held effects (push, pull request) carry node-signed authorizations and outcomes under
  the host's cert-root key, for this pod.

Both keys are the operator's statement. Nothing in this run ties them to hardware:

- executor key `79193ef659f26ad03f62e5c1bf42eafd24e3d44295af26943af1d42ac898dab2`
  (`nucleus-executor/4e15282d61b4c006`), enrolled on 2026-10-05, before this run;
- host cert-root key `c7708cfc1b26771ce116c78555f08ed79f142ca335afcb7e9a3de8ba009b2114`.

How the host was built, which is the operator's account and not something these checks
verify: the host image came from the v2.5.0 tag's host Containerfile (tag commit
`0f2471d5`). It was patched to install the release's `nucleus-node`, `nucleus-mcp` and rootfs
tarballs by their published digests (`release-manifest/release-assets.sha256`). It also
installed a journey guest rootfs (`inputs/rootfs.digest`), built from a digest-pinned harness
image (`inputs/harness-base.txt`, `inputs/Containerfile.harness`) and a guest layer built
from the tag's source (`inputs/guest-layer.digest`), not one taken from the published rootfs.

## Re-verify it yourself

You need `gh`, `cosign` and `jq`. Run this from a checkout of this directory.

```sh
# 1. The published verifier, checked against the release workflow.
mkdir -p rel && cd rel
gh release download v2.5.0 --repo coproduct-opensource/nucleus \
  --pattern 'nucleus-audit-2.5.0-aarch64-apple-darwin.tar.gz*'
cosign verify-blob --bundle nucleus-audit-2.5.0-aarch64-apple-darwin.tar.gz.sigstore.json \
  --certificate-identity https://github.com/coproduct-opensource/nucleus/.github/workflows/release.yml@refs/tags/v2.5.0 \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  nucleus-audit-2.5.0-aarch64-apple-darwin.tar.gz
tar xzf nucleus-audit-2.5.0-aarch64-apple-darwin.tar.gz && cd ..

A=./rel/nucleus-audit
SIGNER=79193ef659f26ad03f62e5c1bf42eafd24e3d44295af26943af1d42ac898dab2
HOSTPUB=c7708cfc1b26771ce116c78555f08ed79f142ca335afcb7e9a3de8ba009b2114
POD=$(cat receipt/pod_id)
VALID=$(( ($(date +%s) + 86400) * 1000000 ))
X=$(mktemp -d)

# 2. Expectations. These come from the run's own admission, so they check that the receipt
#    is consistent with it. A real relying party states its own.
$A prepare-execution --admission receipt/admission.json --signer-key-hex "$SIGNER" \
  --environment-inputs receipt/env-inputs.json --valid-until-micros "$VALID" > $X/expected-receipt.json
for k in a b c; do
  $A prepare-execution --admission receipt/admission.json --signer-key-hex "$SIGNER" \
    --environment-inputs receipt/env-inputs.json --valid-until-micros "$VALID" \
    --artifacts artifacts/artifacts-$k.json > $X/expected-$k.json
done

# 3. The checks. Each should exit 0.
$A verify-execution --receipt receipt/receipt.json --expectations $X/expected-receipt.json
$A verify-logs --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --stdout logs/stdout.bin --stderr logs/stderr.bin
for k in a b c; do
  $A verify-artifacts --bundle artifacts/bundle-$k.json --expectations $X/expected-$k.json
done
$A verify-host-effects --log host-effects/host-effect-authorizations.jsonl \
  --outcomes host-effects/host-effect-outcomes.jsonl --host-pubkey "$HOSTPUB" --pod "$POD"

# 4. The controls. Each should exit 1.
$A verify-execution --receipt receipt/receipt.json --expectations $X/expected-receipt.json --require-attested
$A verify-execution --receipt verify/tamper-inputs/receipt.json --expectations $X/expected-receipt.json
$A verify-artifacts --bundle verify/tamper-inputs/bundle-a.json --expectations $X/expected-a.json
$A verify-logs --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --stdout verify/tamper-inputs/stdout.bin --stderr logs/stderr.bin
$A verify-host-effects --log verify/tamper-inputs/host-effect-authorizations.jsonl \
  --host-pubkey "$HOSTPUB" --pod "$POD"
$A verify-host-effects --log host-effects/host-effect-authorizations.jsonl \
  --host-pubkey "${HOSTPUB%?}0" --pod "$POD"
```

| Control | Refusal |
|---|---|
| `--require-attested` | `the node platform is not attested`: the receipt says `unattested` |
| tampered receipt root hash | `root hash mismatch` |
| tampered artifact (`diff`) | `artifact bytes differ from signed identity` |
| tampered stdout | `Log("stdout")` |
| host-effect record with its declassification stripped | `host signature does not verify` |
| wrong host key | `host signature does not verify` |

`verify/summary.txt` and `verify/outputs/` hold the outputs recorded at the time of the run.

## Layout

- `receipt/`: the signed execution receipt, the admission, the environment inputs and the pod spec.
- `artifacts/`, `logs/`: the signed artifact bundles and the console logs.
- `host-effects/`: the node-signed authorization and outcome records for the held effects.
- `approvals/`: the host-retained reviews of the held effects, the approval event log, the
  decoded push, and who approved each.
- `release-manifest/`: the digests of the published release assets the host used.
- `inputs/`: digests of the guest rootfs, the harness image and the guest layer, and of the
  workspace input.
- `verify/`: the expectations, every verifier output, the tamper inputs, and
  `verify.sh.txt`, the script that produced them. It ran against the working directory
  of the run, not this layout, and is kept as a record. The commands above are the ones
  to run.

`REDACTION.md` lists what was left out, and the identifiers that remain because they are
inside signed content.
