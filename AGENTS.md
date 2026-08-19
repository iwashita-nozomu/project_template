# Repository instructions

This repository is self-contained. Treat tracked project files as the source of truth.

- Preserve the exact registered AgentCanon gitlink, but do not require its checkout, a source resolver, updater, secret, or network call to read or validate the repository.
- Keep project commands in the `Makefile` and project-owned tools under `tools/`.
- Keep environment construction in `docker/Dockerfile`; lifecycle hooks may validate an environment but must not introduce a second dependency source.
- Run `make pr-check` for focused changes and `make fresh-clone-check` when bootstrap or repository structure changes.
- `.codex/` is a read-only static snapshot owned by this repository. Derived repositories do not synchronize it at runtime.
- Update the static snapshot only through an explicit template-maintainer import, with provenance reviewed in the same change.
