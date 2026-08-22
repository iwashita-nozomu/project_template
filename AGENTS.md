# Project Template Repository Instructions

This repository owns the generated project's source, build, test, Docker,
documentation, CI, and local policy. It does not vendor, project, or copy
AgentCanon source, skills, agents, hooks, tests, or runtime state.

## Working boundary

- Make repository changes only beneath this repository root. Generated build,
  test, and report artifacts must use the tracked project-owned paths or the
  ignored `workspace/` area.
- Run project validation through `test/testrunner.sh`; the same entrypoint must
  work in the project image built from `docker/Dockerfile`.
- Do not add an AgentCanon submodule, gitlink, source symlink, static seed,
  source resolver, updater state, or AgentCanon-owned test command.
- Project Docker and CI must work without AgentCanon, credentials, or network
  access beyond dependency/image acquisition during their explicit setup step.

## Optional AgentCanon development

AgentCanon is a separate repository. Only when its source must be changed, use
`scripts/agent-canon-develop.sh clone <qualified-task>` to create an ignored
clone at `workspace/agent-canondevelop/<qualified-task>/agent-canon`, then work
from that Git root and follow its own `AGENTS.md` and top-level `bootstrap.sh`.
Cloning in that bounded workspace is an ordinary in-scope preparation step and
does not require a second permission prompt.

AgentCanon tools, isolated Codex home, eval spool, and `agent-canon-log`
publication remain owned by that clone and its external runtime. They never run
as a hidden prerequisite of project build or test. After merged-main and clean
resource readback, run `scripts/agent-canon-develop.sh cleanup <qualified-task>`;
do not leave the clone, runtime, container, image, or generated binaries behind.

## Completion

Before delivery, inspect the exact diff, run the checks selected by the changed
project responsibility, run the project container test path when Docker or test
behavior changed, and report commands and failures with their environment owner
and repository responsibility. Do not describe an AgentCanon tool-environment
failure as a project-code failure, or the reverse.
