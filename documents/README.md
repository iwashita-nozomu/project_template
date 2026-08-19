# Repository documents

`documents/` contains contracts, design material, durable notes, and external source records owned by this repository. A normal clone carries every project-owned document needed by bootstrap and validation; no document resolver or initialized AgentCanon checkout is required.

## Operational contracts

- [Template bootstrap](contracts/template-bootstrap.md)
- [Template validation](contracts/template-validation.md)
- [Template GitHub remote](contracts/template-github-remote.md)
- [Licensing policy](contracts/licensing-policy.md)
- [Linux and WSL host requirements](contracts/linux-wsl-host-requirements.md)
- [Server host contract](contracts/server-host-contract.md)
- [Remote execution repository contract](contracts/remote-execution-repo-contract.md)

## Design documents

- [Docker environment boundary](design/docker-zero-build-environment.md)
- [GitHub Actions design](design/github-actions.md)
- [Experiment README contract](experiment-readme-contract-r9.md)
- `experiment-readme-contract-r9.json` is the machine-readable schema paired with that contract.

AgentCanon runtime definitions are not duplicated as template documents. The exact source pin and root symlink view are described by the bootstrap and validation contracts; the referenced runtime remains owned by AgentCanon.

## Notes and source records

- [Cross-run notes](notes/README.md)
- [External references](references/README.md)

Notes and source records provide durable context and evidence. They do not replace the contracts and design documents that own repository behavior.

Generated reports and run artifacts do not belong in this directory. Repository-specific additions should be regular files with local links and explicit ownership.
