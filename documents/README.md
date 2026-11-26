# Repository documents

`documents/` contains design material, durable notes, and external source records owned by this repository. A normal clone carries project-owned source and dependency guidance; no bootstrap or external document resolver is required.

## Operational contracts

- [Licensing policy](contracts/licensing-policy.md)

## Agent instructions

[AGENTS.md](../AGENTS.md) is a self-contained tracked file combining the
AgentCanon common instructions and the
[project-specific fragment](agent-canon/consumer-root-instructions.md).
Maintainers regenerate it from the template root with the AgentCanon CLI
and a current source checkout.

```bash
agent-canon compose-consumer-entrypoint \
  --source-root /path/to/agent-canon \
  --base /path/to/agent-canon/ROOT_AGENTS.md \
  --specific documents/agent-canon/consumer-root-instructions.md \
  --output ./AGENTS.md
```

## Design documents

- [Docker dependency example](design/docker-zero-build-environment.md)
- [C++ build layout](design/cpp-build-layout.md)
- [Experiment workflow](design/experiment-workflow.md)

## Notes and source records

- [Cross-run notes](notes/README.md)
- [External references](references/README.md)

Notes and source records provide durable context and evidence. They do not replace the contracts and design documents that own repository behavior.

Generated reports and run artifacts do not belong in this directory. Repository-specific additions should be regular files with local links and explicit ownership.
