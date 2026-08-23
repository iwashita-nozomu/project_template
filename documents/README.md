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
- [C++ build layout](design/cpp-build-layout.md)
- [GitHub Actions design](design/github-actions.md)
- [Experiment workflow](design/experiment-workflow.md)

AgentCanon runtime definitions are not duplicated as template documents. AgentCanon is a separate standalone repository. When its tools are needed, use the ignored task clone and external runtime described by the bootstrap contract; never add its source, symlinks, tests, or runtime state to this tree.

## Notes and source records

- [Cross-run notes](notes/README.md)
- [External references](references/README.md)

Notes and source records provide durable context and evidence. They do not replace the contracts and design documents that own repository behavior.

Generated reports and run artifacts do not belong in this directory. Repository-specific additions should be regular files with local links and explicit ownership.
