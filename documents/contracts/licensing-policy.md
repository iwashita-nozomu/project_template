# Licensing policy

This template repository is licensed under the Apache License 2.0 unless a derived repository deliberately replaces the root `LICENSE` and package metadata.

AgentCanon is registered as an exact Git submodule and retains its own license and source history under `vendor/agent-canon`. The root `AGENTS.md` and `.codex` symlinks are references to that exact checkout; this repository does not relicense or copy the referenced AgentCanon files. An uninitialized checkout contains no AgentCanon file bytes.

When a derived repository changes its project license, update the following in the same change:

- `LICENSE`
- `pyproject.toml` package license metadata, when Python packages are published
- README license text
- project-specific source headers, when the project uses source headers
- release and distribution metadata

Third-party dependencies retain their own license terms. Do not infer that the root license replaces dependency licenses recorded by package managers, submodules, or upstream distributions.
