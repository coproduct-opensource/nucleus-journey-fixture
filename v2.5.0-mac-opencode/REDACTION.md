# What this bundle leaves out, and why

## Excluded

| Item | Why |
|---|---|
| Forge installation tokens and model access tokens | Minted per call outside nucleus, by the operator's forge minter and the cloud's token service. They never reached the pod or any file collected here. A scan of every file, and of every base64 string decoded from them (artifact bundles, approval bodies, Sigstore bundles), for token prefixes, `Bearer`, JWTs, PEM private keys, cloud access keys, private IPs and home-directory paths found nothing. |
| Node private keys and the host's identity directory | Secrets. |
| `workspace.json`, `create.json`, `up.json`, `host.json` | Operational: the node's container-network URL (a private IP), the pod's local proxy address, and the operator's local paths. |
| The operator upstream registry (`upstreams.toml`), the patched host Containerfile, the build scripts and build logs | Operator configuration and build output, with hostnames and paths. README.md describes what the patch did. They are kept privately. |
| `node-records/authority.json`, `budget-consumption.json`, `firecracker.log`, `lifecycle.log` | Node-side records that none of the stranger checks reads. They are kept privately. |
| `collect.*`, `create.err`, `seed.err`, the watcher log, the run timeline | Operational noise with local paths. |
| `verify/artifacts-*/` | The verifier's extracted copies of the artifact bundles: the same bytes as `artifacts/bundle-*.json`. |

Paths in the unsigned verifier output and in `verify/verify.sh.txt` were rewritten to `./` or
`<scratch>/`. No signed file was edited.

## Present, and cannot be redacted without breaking a signature

- **GCP project id `gatehouse-510101`** in the coding-model upstream URL. It appears in
  `receipt/pod.yaml` and in the node-signed `host-effects/host-effect-authorizations.jsonl`.
  The pod spec's digest is bound into the admission and the receipt, so editing it breaks
  `verify-execution` and `verify-host-effects`.
- **The coding-model upstream's hostname and the model id.** The pod spec names the
  operator's coding-model upstream, and the environment inputs name the model the harness
  asked for (`JOURNEY_MODEL`). Both are bound into the admission and the receipt. The
  harness's own log, inside the signed artifact bundles, also names its model-provider
  adapter. Nucleus chooses none of these; the operator's journey configuration does.
- **The node's container-internal scratch path** (`/srv/state/scratch/workspace-<uuid>.ext4`)
  in the pod spec. It names no host or person.
- **The fixture repository, branch and PR** (public).
