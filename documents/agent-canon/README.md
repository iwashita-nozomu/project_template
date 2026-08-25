# AgentCanon consumer composition

`consumer-root-instructions.md` is the only project-specific source fragment
for the root `AGENTS.md`. It is intentionally below `documents/` and is not an
auto-discovered instruction entrypoint.

The committed root `AGENTS.md` is a regular, self-contained file. It contains
the AgentCanon `ROOT_AGENTS.md` common base first and this fragment second,
with a source-commit provenance marker. There is no `AGENT.md`, symlink,
vendor copy, submodule, or live runtime dependency.

A maintainer regenerates the file by supplying an explicit AgentCanon source
checkout:

```bash
./tools/compose_agent_instructions.sh /path/to/agent-canon
```

The command uses the public `compose-consumer-entrypoint` tool from that
checkout. It does not fetch AgentCanon or update consumer files implicitly.
