# Repository bootstrap scripts

`init_from_template.sh` performs the offline identity conversion. `start_repository.sh` adds a preview and read-only post-commit validation wrapper.

Neither script clones another repository, resolves an AgentCanon source root,
contacts a registry, reads a credential, or modifies global Codex state.
AgentCanon editing is a separate explicit workflow in the ignored
`workspace/agent-canondevelop/<qualified-task>/agent-canon` clone; the project
bootstrap never starts or cleans that runtime implicitly.
