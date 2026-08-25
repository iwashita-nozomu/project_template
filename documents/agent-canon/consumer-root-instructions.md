# Consumer-specific instructions

This section is owned by the `project_template` repository and is appended to
the common AgentCanon consumer base when the root `AGENTS.md` is regenerated.
It is a source fragment, not a root instruction entrypoint; keep it under
`documents/` so it is not discovered as an additional agent instruction file.

## Repository responsibility

This repository owns the generated project's source, build, tests, Docker,
documentation, CI, and local policy. External tool and runtime repositories
are not part of this checkout.

## Working boundary

- Make repository changes only beneath this repository root. Generated build,
  test, and report artifacts must use tracked project-owned paths or the
  ignored `workspace/` area.
- Run project validation through `test/testrunner.sh`; the same entrypoint must
  work in the project image built from `docker/Dockerfile`.
- Project Docker and CI must work from this checkout and their explicit setup
  inputs without hidden external repository state.

## Completion evidence

Before delivery, inspect the exact diff, run the checks selected by the changed
project responsibility, run the project container test path when Docker or
test behavior changed, and report commands and failures with their environment
owner and repository responsibility.

## AgentCanon composition maintenance

The root `AGENTS.md` is a generated regular file composed from the AgentCanon
`ROOT_AGENTS.md` base followed by this fragment. Regenerate it only through the
explicit maintainer command below, passing the AgentCanon source checkout as
its argument:

```bash
./tools/compose_agent_instructions.sh /path/to/agent-canon
```

The committed root file must remain self-contained and usable without an
AgentCanon checkout, runtime, vendor directory, submodule, live projection, or
symlink. Do not add a singular `AGENT.md` or make the root `AGENTS.md` a
symlink. The composer records the AgentCanon source commit as provenance; it
does not create a runtime dependency or an automatic updater for this
consumer file.
