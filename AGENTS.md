# Project Template Repository Instructions

This repository owns the generated project's source, build, test, Docker,
documentation, CI, and local policy. External tool and runtime repositories are
not part of this checkout.

## Working boundary

- Make repository changes only beneath this repository root. Generated build,
  test, and report artifacts must use the tracked project-owned paths or the
  ignored `workspace/` area.
- Run project validation through `test/testrunner.sh`; the same entrypoint must
  work in the project image built from `docker/Dockerfile`.
- Project Docker and CI must work from this checkout and their explicit setup
  inputs without hidden external repository state.

## Completion

Before delivery, inspect the exact diff, run the checks selected by the changed
project responsibility, run the project container test path when Docker or test
behavior changed, and report commands and failures with their environment owner
and repository responsibility.
