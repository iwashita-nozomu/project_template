# Template validation contract

The repository owns two normal validation entry points:

- `bash test/testrunner.sh` runs the complete static, tooling, Docker-contract,
  and C++ list;
- `bash tools/check_fresh_clone.sh` validates an initialized ordinary
  source-free descendant clone.

Targeted CMake development uses `cmake --preset dev`,
`cmake --build --preset dev`, and `ctest --preset dev`.

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
