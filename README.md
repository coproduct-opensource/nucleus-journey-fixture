# nucleus-journey-fixture

Target repository for nucleus's end-to-end release journeys
([coproduct-opensource/nucleus](https://github.com/coproduct-opensource/nucleus),
`examples/coding-journey`).

An AI agent running inside a nucleus pod receives `TASK.md`, repairs `summary.py`,
runs the unchanged `test_summary.py`, and opens a pull request here through the
host's mediated egress, using a short-lived, repository-scoped token minted per
call. Every such pull request is evidence from a test run. They are closed, not
merged, and `main` stays at the unrepaired baseline so each run starts from the
same state.

The initial test suite fails on purpose: passing it is the agent's work.
