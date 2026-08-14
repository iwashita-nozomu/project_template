# Repository bootstrap scripts

`init_from_template.sh` performs the offline identity conversion. `start_repository.sh` adds a preview and read-only post-commit validation wrapper.

Neither script clones another repository, initializes a submodule, resolves a source root, contacts a registry, reads a credential, or updates the static `.codex` seed.
