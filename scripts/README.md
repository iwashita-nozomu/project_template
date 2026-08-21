# Repository bootstrap scripts

`init_from_template.sh` performs the offline identity conversion. `start_repository.sh` adds a preview and read-only post-commit validation wrapper.

Neither script clones another repository, initializes the registered submodule, resolves a source root, contacts a registry, reads a credential, or updates the static `.codex` seed. Initialization preserves the exact registration and gitlink without turning them into a default runtime dependency.
