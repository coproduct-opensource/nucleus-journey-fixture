# v2.6.0, attested x86_64 node, aider

| | |
|---|---|
| Release | [v2.6.0](https://github.com/coproduct-opensource/nucleus/releases/tag/v2.6.0), published assets only |
| Node | x86_64 GCP Shielded VM `nucleus-attest-node-202610070156` (Secure Boot, vTPM). Deleted at 2026-10-07T02:16:31Z |
| Harness | aider 0.86.2, in a Firecracker pod (`310ce4d2-2f1e-4d80-b74e-5e485bd7da1e`) |
| Result | https://github.com/coproduct-opensource/nucleus-journey-fixture/pull/4 (a fixture repository; its PRs stay open and are never merged) |
| Platform tier | **Attested** with the operator's AK pin; **Unattested** without it |
| AK anchor | **`operator_fetched`** (`gcp-shielded-vm-identity:nucleus-attest-node-202610070156`) |
| Verifier | `nucleus-audit` 2.6.0, `aarch64-apple-darwin`: a different machine and CPU architecture from the node |

A coding agent repaired `summary.py` in the fixture repository. The pod held no forge
credential. The push and the pull request went out through host-performed egress, and the
host held each one until the owner approved it (`approvals/APPROVAL_ATTRIBUTION.txt`). The
node ran only the published v2.6.0 release bytes. `inputs/` ties its install directory to the
signed release tarballs.

## What the verdict says, and what it rests on

`verify-execution --require-attested`, checked against the published, cosign-verified
`nucleus-2.6.0-x86_64.node-reference.json`, returns:

- verdict `authorized_on_an_attested_node`, tier `attested`, EAR status `affirming`;
- anchor `operator_fetched`, source `gcp-shielded-vm-identity:nucleus-attest-node-202610070156`;
- in the IMA scope `/usr/local/bin`: `nucleus-node` `95abe8cf…`, `firecracker` `99ad0f5c…`
  and `jailer` `65ef226e…`, all on the release allowlist, with no divergences;
- 64 kernel modules listed under `ima_not_in_scope`. The platform's Secure Boot policy
  measured them, and the release vouches for none of them;
- `not_checked`: Secure Boot, EFI applications, boot files and the kernel command line. The
  release publishes no host image, so the release manifest does not check any of these, and
  this result says nothing about the host's boot.

**The trust assumption is the AK pin.** This VM type has no platform-issued AK or EK
certificate, so nothing a stranger can check cryptographically ties the quote's attestation
key to a TPM. The pin

```
gcp-shielded-vm-identity:nucleus-attest-node-202610070156=6e8ab634f572c777352d62e2f6a7da1b53fc9d2ae8bd3d667a4a0646a744ef8d
```

is the operator's statement that the cloud provider's authenticated `get-shielded-identity`
API reported, for this VM, an AK whose SubjectPublicKeyInfo has that SHA-256. The operator
fetched it while the VM existed. The VM has since been deleted, so nobody can fetch it again:
an `Attested` reading of this run is exactly as good as your trust in the operator's
statement. The same digest appears inside the quote (`quote.ak_spki_sha256`). Copying it
from there instead would be circular, because the evidence would then vouch for its own key.

With no pin, the same check returns `Unattested` (`ak_unanchored: no_matching_operator_pin`).

The other operator-supplied input is the host-effect signing key (cert root)
`c80b7a5b991858937f16eb93e254cad1432df7b1483af57a93dc1eebf2b393da`, which
`verify-host-effects` needs. The executor key
`6b2248863d28ed3fe824706db9fd72d58364da7b8f8097a6f1d685b34b9630b7`
(`node-evidence/node-keys.json`, from the node's public `/v1/node/keys`) is bound into the
TPM quote, and the verifier refuses evidence that binds a different one.

## Re-verify it yourself

You need `gh`, `cosign`, `jq` and `openssl`. Run this from a checkout of this directory.

```sh
# 1. The published verifier and reference manifest, checked against the release workflow.
mkdir -p rel && cd rel
gh release download v2.6.0 --repo coproduct-opensource/nucleus \
  --pattern 'nucleus-audit-2.6.0-aarch64-apple-darwin.tar.gz*' \
  --pattern 'nucleus-2.6.0-x86_64.node-reference.json*'
for f in nucleus-audit-2.6.0-aarch64-apple-darwin.tar.gz nucleus-2.6.0-x86_64.node-reference.json; do
  cosign verify-blob --bundle "$f.sigstore.json" \
    --certificate-identity https://github.com/coproduct-opensource/nucleus/.github/workflows/release.yml@refs/tags/v2.6.0 \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com "$f"
done
tar xzf nucleus-audit-2.6.0-aarch64-apple-darwin.tar.gz && cd ..
cmp rel/nucleus-2.6.0-x86_64.node-reference.json release-manifest/nucleus-2.6.0-x86_64.node-reference.json

A=./rel/nucleus-audit
RREF=./rel/nucleus-2.6.0-x86_64.node-reference.json
PIN='gcp-shielded-vm-identity:nucleus-attest-node-202610070156=6e8ab634f572c777352d62e2f6a7da1b53fc9d2ae8bd3d667a4a0646a744ef8d'
SIGNER=$(jq -r .executor.public_key_hex node-evidence/node-keys.json)
HOSTPUB=c80b7a5b991858937f16eb93e254cad1432df7b1483af57a93dc1eebf2b393da
FED=$(jq -r .binding.federation.jwks_sha256 node-evidence/evidence-epoch.json)
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
$A verify-execution --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --node-evidence node-evidence/evidence-epoch.json --node-reference "$RREF" \
  --operator-pin "$PIN" --require-attested
$A verify-node-evidence --evidence node-evidence/evidence-challenge.json --reference "$RREF" \
  --executor-ed25519 "$SIGNER" --federation "$FED" \
  --nonce "$(cat node-evidence/challenge-nonce.txt)" --operator-pin "$PIN"
$A verify-logs --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --stdout logs/stdout.bin --stderr logs/stderr.bin
for k in a b c; do
  $A verify-artifacts --bundle artifacts/bundle-$k.json --expectations $X/expected-$k.json
done
$A verify-host-effects --log host-effects/host-effect-authorizations.jsonl \
  --outcomes host-effects/host-effect-outcomes.jsonl --host-pubkey "$HOSTPUB" --pod "$POD"

# 4. The controls. Each should exit 1.
$A verify-execution --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --node-evidence node-evidence/evidence-epoch.json --node-reference "$RREF" --require-attested     # no pin
$A verify-execution --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --node-evidence node-evidence/evidence-epoch.json --node-reference "$RREF" \
  --operator-pin "${PIN%?}0" --require-attested                                                     # wrong pin
$A verify-execution --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --node-evidence node-evidence/evidence-epoch.json \
  --node-reference verify/tamper-inputs/manifest-wrong-node-digest.json \
  --operator-pin "$PIN" --require-attested                                                          # Contested
$A verify-execution --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --node-evidence verify/tamper-inputs/evidence-epoch.json --node-reference "$RREF" \
  --operator-pin "$PIN" --require-attested                                                          # evidence not named by the receipt
$A verify-node-evidence --evidence node-evidence/evidence-challenge.json --reference "$RREF" \
  --executor-ed25519 "$SIGNER" --federation "$FED" --nonce "$(openssl rand -hex 32)" \
  --operator-pin "$PIN"                                                                             # replayed challenge
$A verify-node-evidence --evidence node-evidence/evidence-epoch.json --reference "$RREF" \
  --executor-ed25519 "$SIGNER" --federation "$FED" --max-age-secs 900 \
  --receipt-time $(( $(jq .freshness.epoch.iat node-evidence/evidence-epoch.json) + 3600 )) \
  --operator-pin "$PIN"                                                                             # stale epoch
$A verify-node-evidence --evidence node-evidence/evidence-challenge.json --reference "$RREF" \
  --executor-ed25519 "$SIGNER" --nonce "$(cat node-evidence/challenge-nonce.txt)" \
  --operator-pin "$PIN"                                                                             # no --federation
$A verify-execution --receipt verify/tamper-inputs/receipt.json --expectations $X/expected-receipt.json
$A verify-artifacts --bundle verify/tamper-inputs/bundle-a.json --expectations $X/expected-a.json
$A verify-logs --receipt receipt/receipt.json --expectations $X/expected-receipt.json \
  --stdout verify/tamper-inputs/stdout.bin --stderr logs/stderr.bin
$A verify-host-effects --log verify/tamper-inputs/host-effect-authorizations.jsonl \
  --host-pubkey "$HOSTPUB" --pod "$POD"
$A verify-host-effects --log host-effects/host-effect-authorizations.jsonl \
  --host-pubkey "${HOSTPUB%?}0" --pod "$POD"                                                       # wrong host key
```

The 12 controls are refused for these reasons. `verify/summary.txt` and `verify/outputs/`
hold the outputs recorded at the time of the run.

| Control | Refusal |
|---|---|
| no pin, wrong pin | `Unattested`: `ak_unanchored: no_matching_operator_pin` |
| manifest with `nucleus-node`'s digest altered | `Contested`: `ima_file_not_allowed` + `ima_required_missing` |
| evidence not named by the receipt | its SHA-256 is not `160dddd0…7958` |
| replayed challenge, stale epoch | `Expired`: `nonce_mismatch`, `too_old` |
| no `--federation` | refused, naming the bound JWKS digest `104818fd…e4f3` |
| tampered receipt root hash, artifact, stdout | `root hash mismatch`, `artifact bytes differ from signed identity`, `Log("stdout")` |
| tampered host-effect record, wrong host key | `host signature does not verify` |

## Layout

- `receipt/`: the signed execution receipt, the admission, the environment inputs and the pod spec.
- `node-evidence/`: the evidence document the receipt names (SHA-256 `160dddd0…7958`), fetched
  from the node's anonymous public listener and byte-identical to the mTLS copy. Also a fresh
  challenge quote with its nonce, and the node's public keys.
- `artifacts/`, `logs/`: the signed artifact bundles and the console logs.
- `host-effects/`: the node-signed authorization and outcome records for the held effects.
- `approvals/`: the host-retained reviews of both held effects, the decoded push, and who
  approved each. On v2.6.0 a pending approval lives 1800 s.
- `release-manifest/`: the published manifest, its Sigstore bundle, and the cosign and SLSA
  results for every asset the node used.
- `inputs/`: digests that tie the node's install, kernel, rootfs and guest layer to the
  published bytes.
- `verify/`: the expectations, every verifier output, the tamper inputs, and
  `verify.sh.txt`, the script that produced them. It ran against the working directory
  of the run, not this layout, and is kept as a record. The commands above are the ones
  to run.

`REDACTION.md` lists what was left out, and the identifiers that remain because they are
inside signed content.
