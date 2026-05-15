<!--
@dependency-start
responsibility Documents documents/ for this repository.
upstream design ../vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md documents ownership policy
upstream design ../vendor/agent-canon/documents/shared-runtime-surfaces.toml machine-readable ownership manifest
upstream design ../vendor/agent-canon/documents/algorithm-implementation-boundary.md algorithm math-to-code boundary policy
upstream design ../vendor/agent-canon/documents/codex-configuration-reference.md Codex configuration reference
upstream design ../vendor/agent-canon/documents/object-oriented-design.md general OOP coding policy
upstream design ../vendor/agent-canon/documents/agent-canon-parent-repo-latest-checklist.md parent repo latest-state checklist
upstream design ../vendor/agent-canon/documents/agent-canon-licensing-policy.md AgentCanon licensing boundary
downstream design ./licensing-policy.md repository license boundary
@dependency-end
-->

# documents/

`documents/` is a mixed documentation directory. The root `documents/README.md`
is repo-local and should stay a regular file after template clone. AgentCanon may
seed this file, but derived repositories own their local index.

## Ownership Matrix

| Class | Examples | Edit source |
| --- | --- | --- |
| AgentCanon-owned shared policy source | coding conventions, review process, workflow-supporting policies, shared templates, tool docs | `vendor/agent-canon/documents/` |
| Template-owned active contract | bootstrap, host requirements, server contract, remote execution contract, template remote policy, licensing boundary | root `documents/` regular files |
| Project-owned docs | architecture notes, project-specific design specs, implementation contracts | root `documents/` regular files |
| Generated or run artifacts | agent reports, experiment outputs, logs | `reports/` or `experiments/`, not `documents/` |

If a file is AgentCanon-owned, edit the source under `vendor/agent-canon/`. If a
file is a template-owned active contract, edit the root regular file.

## Canon Runtime References

- [Shared Runtime Surfaces](../vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md): owner classes,
  symlink/copy/regular behavior, and root-view repair rules.
- [Shared Runtime Surface Manifest](../vendor/agent-canon/documents/shared-runtime-surfaces.toml):
  machine-readable surface ownership list.
- [AgentCanon Parent Repository Latest-State Checklist](../vendor/agent-canon/documents/agent-canon-parent-repo-latest-checklist.md):
  task-start checklist for repos that vendor AgentCanon.
- [Codex Configuration Reference](../vendor/agent-canon/documents/codex-configuration-reference.md): Codex CLI
  / config schema / hooks / MCP / skills / subagents reference.
- [AgentCanon GitHub Remote](../vendor/agent-canon/documents/agent-canon-github-remote.md): GitHub canonical
  remote and local bare mirror compatibility.
- [GitHub Copilot Configuration](../vendor/agent-canon/documents/github-copilot-configuration.md): Copilot
  repository instructions, path-specific instructions, custom agents, MCP, setup
  workflow, and PR template routing.

## Coding Policy References

- [Algorithm Implementation Boundary Policy](../vendor/agent-canon/documents/algorithm-implementation-boundary.md):
  math/specification boundary, implementation boundary, change classes, and
  review gates.
- [Object-Oriented Design Policy](../vendor/agent-canon/documents/object-oriented-design.md): class,
  dataclass, Protocol, composition, and inheritance policy.
- [Python Coding Conventions](../vendor/agent-canon/documents/coding-conventions-python.md): Python-specific
  implementation rules.
- [Project Coding Conventions](../vendor/agent-canon/documents/coding-conventions-project.md): project-wide
  environment, dependency, and runtime rules.

## Template-Owned Active Contracts

These files should be regular files in the template or derived repo root:

- [Template Bootstrap](./template-bootstrap.md)
- [Licensing Policy](./licensing-policy.md)
- [Template GitHub Remote](./template-github-remote.md)
- [Linux / WSL Host Requirements](./linux-wsl-host-requirements.md)
- [Server Host Contract](./server-host-contract.md)
- [Remote Execution Repo Contract](./remote-execution-repo-contract.md)

AgentCanon provides reusable contract templates under
[templates/](../vendor/agent-canon/documents/templates/),
but the active contract for a derived repo belongs to that repo.

## Tooling And Artifact References

- [Result Log Retention And Visualization](../vendor/agent-canon/documents/result-log-retention-and-visualization.md):
  run result, summary, visualization artifact, and retention rules.
- [Repo-Local Tool Imports](../vendor/agent-canon/documents/repo-local-tool-imports.md): disposition ledger for
  tools that grow in derived repos before AgentCanon promotion.
