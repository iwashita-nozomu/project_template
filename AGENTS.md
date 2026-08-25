<!-- agent-canon:consumer-root-agents:v1 -->
<!-- agent-canon:source-commit=8be93bbc5e8efcc461013e5972b653f49f6dc6f6 -->
<!-- agent-canon:base-sha256=c1f4f2ea9fa6db66eb5ce09e99d54a1717645aa98ef0d5ade735b7f84506751f -->
<!-- agent-canon:base-bytes=3884 -->
<!-- agent-canon:specific-sha256=e2b0e7899515ae2643ec5d5b7c6dbf9f7f045ac2667e9ee2f7c8c631337cf6a8 -->
<!-- agent-canon:specific-bytes=2071 -->
<!-- agent-canon:consumer-root-base:start -->
# AgentCanon Consumer Instructions

<!--
@dependency-start
contract agent-runtime
responsibility Provides the common, source-free base for a consumer repository's generated root AGENTS.md.
upstream design documents/design/entrypoint-owner-map.md root entrypoint grammar and consumer composition boundary
upstream design documents/conventions/software-engineering-principles.md contract-complete engineering decision policy
downstream implementation tools/agent_tools/entrypoint_composer.py composes the regular consumer root file
downstream implementation tools/agent_tools/check_entrypoint_owner_map.py validates the base grammar
@dependency-end
-->

This is the common base for a consumer repository's root `AGENTS.md`. The
consumer keeps that generated file as a regular tracked file by composing this
base with its own specific instructions. The composition is an explicit
consumer maintenance operation; it is not a live AgentCanon projection,
runtime import, updater, vendor checkout, submodule, or symlink.

## Repository Role

The consumer repository owns its product source, build environment, tests,
documentation, CI, and tracked instruction extension. AgentCanon does not
become a second source of truth for those surfaces. The generated root file is
self-contained after it is committed and remains usable when the AgentCanon
source checkout and runtime are unavailable.

## Reader Map

| Task intent | Consumer-owned reader |
| --- | --- |
| product implementation and behavior | the consumer's source and design owners |
| build, test, and execution environment | the consumer's build and test owners |
| repository structure and file responsibility | the consumer's structure documentation |
| consumer-specific agent instructions | the appended consumer-owned section of this file |
| AgentCanon maintenance | a separately selected AgentCanon development checkout |

## Always-On Boundary

The explicit user request and the current consumer-owned canonical owner are
the source of truth. Preserve unknown dirty, staged, untracked, branch, and
worktree state until the consumer's Git safety owner classifies it. Keep
product behavior, environment policy, tests, CI, credentials, and runtime
semantics with their consumer owners.

This common base only establishes the consumer instruction boundary. It does
not re-own task procedures, command recipes, role lifecycles, implementation
policy, validation schemas, or AgentCanon source-editing policy. Those details
belong to the consumer-specific section or the consumer's own canonical owner.

## Runtime Owner Map

| Responsibility | Consumer canonical owner | Validation / reader route |
| --- | --- | --- |
| product implementation and behavior | consumer source and design owners | consumer implementation route |
| build, tests, and runtime environment | consumer build and test owners | consumer execution route |
| repository structure and file placement | consumer structure owner | consumer structure route |
| root instruction extension | consumer-specific section in this file | consumer instruction route |
| AgentCanon source maintenance | selected AgentCanon development checkout | AgentCanon maintenance route |

## Task Entry

Start with this common base and the appended consumer-specific instructions.
Resolve the task owner and the consumer validation oracle from those surfaces.
When the task changes AgentCanon itself, move to a qualified AgentCanon
development checkout and keep the consumer tree unchanged unless the consumer
task explicitly owns the resulting generated file.

## Validation Routing

Use the validation route owned by the changed consumer responsibility. Validate
the changed contract and its failure semantics, then use the consumer's normal
closeout route when required. A generated root file does not authorize
unrelated AgentCanon checks, product checks, or runtime changes.

<!-- agent-canon:consumer-root-base:end -->
<!-- agent-canon:consumer-root-specific:start -->
# Consumer-specific instructions

This section is owned by the `project_template` repository and is appended to
the common AgentCanon consumer base when the root `AGENTS.md` is regenerated.
It is a source fragment, not a root instruction entrypoint; keep it under
`documents/` so it is not discovered as an additional agent instruction file.

## Repository responsibility

This repository owns the generated project's source, build, tests, Docker,
documentation, CI, and local policy. External tool and runtime repositories
are not part of this checkout.

## Working boundary

- Make repository changes only beneath this repository root. Generated build,
  test, and report artifacts must use tracked project-owned paths or the
  ignored `workspace/` area.
- Run project validation through `test/testrunner.sh`; the same entrypoint must
  work in the project image built from `docker/Dockerfile`.
- Project Docker and CI must work from this checkout and their explicit setup
  inputs without hidden external repository state.

## Completion evidence

Before delivery, inspect the exact diff, run the checks selected by the changed
project responsibility, run the project container test path when Docker or
test behavior changed, and report commands and failures with their environment
owner and repository responsibility.

## AgentCanon composition maintenance

The root `AGENTS.md` is a generated regular file composed from the AgentCanon
`ROOT_AGENTS.md` base followed by this fragment. Regenerate it only through the
explicit maintainer command below, passing the AgentCanon source checkout as
its argument:

```bash
./tools/compose_agent_instructions.sh /path/to/agent-canon
```

The committed root file must remain self-contained and usable without an
AgentCanon checkout, runtime, vendor directory, submodule, live projection, or
symlink. Do not add a singular `AGENT.md` or make the root `AGENTS.md` a
symlink. The composer records the AgentCanon source commit as provenance; it
does not create a runtime dependency or an automatic updater for this
consumer file.

<!-- agent-canon:consumer-root-specific:end -->
