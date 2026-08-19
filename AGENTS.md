# Repository instructions

This repository is self-contained. Treat tracked project files as the source of truth.

- Treat AgentCanon submodule registration as optional source identity, not as a default runtime dependency. The admitted states are no registration, or the exact `.gitmodules` entry plus the sole mode-`160000` `vendor/agent-canon` gitlink. Preserve whichever admitted state is present without initializing or consuming the checkout.
- Do not restore AgentCanon root projections, `notes/` or `tests/` projections, updater state, or tracked `.agent-canon/` runtime state.
- Keep project commands in the `Makefile` and project-owned tools under `tools/`.
- Keep environment construction in `docker/Dockerfile`; lifecycle hooks may validate an environment but must not introduce a second dependency source.
- Run `make pr-check` for focused changes and `make fresh-clone-check` when bootstrap or repository structure changes.
- `.codex/` is a read-only static snapshot owned by this repository. Derived repositories do not synchronize it at runtime.
- Update the static snapshot only through an explicit template-maintainer import, with provenance reviewed in the same change.
