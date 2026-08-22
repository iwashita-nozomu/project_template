# Licensing policy

This template repository is licensed under the Apache License 2.0 unless a derived repository deliberately replaces the root `LICENSE` and package metadata.

AgentCanon is a separate repository and retains its own license and source
history. This repository does not vendor, submodule, symlink, copy, or relicense
AgentCanon files. A normal project checkout contains no AgentCanon source bytes.
When a task needs AgentCanon, its separately cloned source and external runtime
remain outside the tracked parent tree and are removed at task closeout.

When a derived repository changes its project license, update the following in the same change:

- `LICENSE`
- `pyproject.toml` package license metadata, when Python packages are published
- README license text
- project-specific source headers, when the project uses source headers
- release and distribution metadata

Third-party dependencies retain their own license terms. Do not infer that the root license replaces dependency licenses recorded by package managers, submodules, or upstream distributions.
