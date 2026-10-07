# What this bundle leaves out, and why

## Excluded
| Item | Why |
|---|---|
| Forge installation tokens and model access tokens | Minted per call outside nucleus (the Gatehouse forge minter, GCP STS). They never reached the pod or any file collected here. A scan of every file and every base64-decoded artifact for token prefixes, `Bearer`, JWTs and PEM private keys found nothing. |
| Node private keys (executor, cert root, approval, federation `jwt_svid_p256_signing_key.der`) | Secrets. The federation key copy was shredded on the node and lived only on the VM's boot disk, which was deleted with the VM. |
| The operator AK pin file and the `get-shielded-identity` API response | Operator input. The pin's value is stated in README.md as the operator's statement, which is what it is. The AK's SPKI digest also appears inside the evidence and the EAR (`quote.ak_spki_sha256`) as an intrinsic part of the quote, so it is not secret. The pin is worth something only because it comes from the operator, not from the evidence. |
| Node client TLS identity (CLI cert/key, trust bundle), `/etc/nucleus/node.env` secrets | Secrets / operator configuration. |
| Operator upstream registry (`upstreams.toml`) | Operator configuration: WIF pool/provider resource names, project number, minter endpoint. |
| Internal / external IPs of the VM, Mac-local scratch paths, node home paths | Infrastructure detail. Paths in unsigned verifier text were rewritten to `./`, `<scratch>/` or `~/`. No IPs appear in the bundle. |
| Stage logs (`stage1.log`, `stage2.log`), `collect.err`, `create.err`, `seed.*`, watcher log, node journal | Operational noise with hostnames and paths. They are kept privately in the run directory. |
| `evidence-epoch.json` fetched over mTLS | Byte-identical to the public-listener copy included (`cmp` equal). |
| Attempt 1 (pod 4f38806a) | The model's repair failed one test (large-decimal precision), so the guest skipped publishing and nothing was held. Kept privately. It is not part of the journey that produced the PR. |

## Present, and cannot be redacted without breaking a signature (owner decision)
- **GCP project id `gatehouse-510101`** in the coding-model upstream URL. It appears in `receipt/pod.yaml`
  and in the node-signed `host-effects/host-effect-authorizations.jsonl`. The pod spec digest is bound
  into the admission and the receipt, so editing it breaks `verify-execution` / `verify-host-effects`.
- **Node VM name `nucleus-attest-node-202610070156`** as the AK anchor label inside the TPM evidence and
  the EAR (`operator_fetched.source`). This is evidence content. The VM has been deleted.
- **Federation issuer `https://nucleus-dev-microvm-host.federation.invalid`** and its JWKS digest
  `104818fd…e4f3` (binding). The `.invalid` name is a non-resolving label, and the JWKS is public by design.
- **The coding-model upstream's hostname and the model id.** The pod spec names the
  operator's coding-model upstream, and the environment inputs name the model the harness
  asked for (`JOURNEY_MODEL`). Both are bound into the admission and the receipt. The harness's
  own log, inside the signed artifact bundles, also names its model-provider adapter. Nucleus
  chooses none of these; the operator's journey configuration does.
- **Fixture repository / branch / PR #4** (public).
