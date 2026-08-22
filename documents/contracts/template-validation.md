# Template validation contract

The repository owns its normal validation entry points:

- `make docs-check` verifies reader-facing local links;
- `make cpp-test` builds and runs the parent CTest surface;
- `make test` runs parent repository tooling tests;
- `make pr-check` composes the pull-request gate;
- `make fresh-clone-check` validates an ordinary source-free descendant clone
  when the project provides that acceptance check.

Project checks do not initialize a submodule, resolve an AgentCanon source
root, load Codex hooks, contact `agent-canon-log`, or inspect an external
AgentCanon checkout. Project Docker validation uses the tracked
`docker/Dockerfile` and the parent test runner.

## Fresh-clone boundary

The fresh-clone check starts from a clean committed tree and validates exactly
what a user receives from an ordinary clone. It may use a temporary local bare
remote, but it does not use recursive clone options, AgentCanon credentials, a
vendor checkout, or root symlink projections. Docker execution is explicit and
is limited to the project image.

## Optional AgentCanon validation

AgentCanon changes are validated in the standalone AgentCanon checkout, using
the runtime profile selected by AgentCanon. That validation is not a parent
repository gate. The AgentCanon source clone lives at
`workspace/agent-canondevelop/<qualified-task>/agent-canon`; runtime state lives
at the corresponding external runtime root. Eval evidence is collected and,
when authorized, synchronized to `agent-canon-log` by AgentCanon itself.

The two validation planes must not be conflated: a failure must identify the
executed command, the owning repository, and whether the responsibility belongs
to the parent project or AgentCanon.
