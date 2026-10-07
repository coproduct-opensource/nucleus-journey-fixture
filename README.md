# Release-journey evidence

This `evidence` branch is separate from `main`. `main` is the fixture's baseline, which the
journeys clone, and this branch shares no history with it.

Each directory holds one run of a coding agent in a nucleus pod on a published release. Each
run's directory keeps the signed records exactly as the node wrote them, so that anyone can
re-check them with that release's published `nucleus-audit` and nothing else. The method is
[Verifying a receipt as a stranger](https://github.com/coproduct-opensource/nucleus/blob/main/docs/stranger-verification.md). Each run's README gives the
exact commands.

In every run, an agent repaired `summary.py` in this repository's `main` baseline
(`9c052db1`). The pod
held no forge credential. The node performed the push and the pull request itself, and held
each one until the owner approved it.

| Run | Release | Node | Harness | Platform tier | AK anchor | Result |
|---|---|---|---|---|---|---|
| [v2.6.0-attested-aider](v2.6.0-attested-aider/README.md) | v2.6.0 | x86_64 GCP Shielded VM, vTPM | aider | **Attested** with the operator's AK pin; Unattested without it | `operator_fetched` | [PR #4](https://github.com/coproduct-opensource/nucleus-journey-fixture/pull/4) |
| [v2.5.0-mac-aider](v2.5.0-mac-aider/README.md) | v2.5.0 | aarch64 Apple `container` dev host, no TPM | aider | **Unattested** | none | [PR #1](https://github.com/coproduct-opensource/nucleus-journey-fixture/pull/1) |
| [v2.5.0-mac-opencode](v2.5.0-mac-opencode/README.md) | v2.5.0 | aarch64 Apple `container` dev host, no TPM | opencode | **Unattested** | none | [PR #2](https://github.com/coproduct-opensource/nucleus-journey-fixture/pull/2) |

What these runs do not show:

- **The attested run rests on the operator's AK pin.** The VM type has no platform-issued
  AK certificate, so the pin is the operator's report of what the cloud API returned while
  the VM existed. The VM has since been deleted, so nobody can fetch the pin again.
- **The Mac runs are Unattested.** Their receipts record that the node had no TPM, so they
  make no claim about the host's boot or binaries.
- **No run checks the host's boot.** The release manifest does not check Secure Boot, EFI
  applications, boot files or the kernel command line, and lists each of them as
  `not_checked`. The release publishes no host image, so those reference values are the
  operator's to supply.

Each run's `REDACTION.md` lists what was left out, and the identifiers that remain because
they are inside signed content.
