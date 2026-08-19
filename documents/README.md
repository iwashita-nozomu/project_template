# Repository documents

`documents/` contains contracts, design material, and tracked supporting notes owned by this repository. A normal clone carries every document needed by the default bootstrap and validation paths; no document resolver or parent checkout is required.

## Cross-run notes

- [Notes hub](notes/README.md)
  - Holds cross-run knowledge, comparisons, and supporting decisions before they are promoted to an owning contract or design document.
  - It is a responsibility directory under `documents/`, not a second root-level document owner.

## Operational contracts

- [Template bootstrap](contracts/template-bootstrap.md)
- [Template validation](contracts/template-validation.md)
- [Template GitHub remote](contracts/template-github-remote.md)
- [Licensing policy](contracts/licensing-policy.md)
- [Linux and WSL host requirements](contracts/linux-wsl-host-requirements.md)
- [Server host contract](contracts/server-host-contract.md)
- [Remote execution repository contract](contracts/remote-execution-repo-contract.md)
- [Legacy live AgentCanon descendant migration](contracts/legacy-live-agent-canon-migration.md)

## Design documents

- [Docker environment boundary](design/docker-zero-build-environment.md)
- [Template static-seed import transaction](design/template-static-seed-import.md)
- [Experiment README contract](experiment-readme-contract-r9.md)
- `experiment-readme-contract-r9.json` is the machine-readable schema paired with that contract.

Generated reports and run artifacts do not belong in this directory. Repository-specific additions should be regular files with local links and explicit ownership. Canonical rules and designs remain in their owning responsibility directories; `documents/notes/` does not replace those owners.
