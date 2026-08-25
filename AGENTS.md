# Project Template Repository Instructions

作業開始時は、まず `~/agent-canon/ROOT_AGENTS.md` を読み、共通の作業規約と
owner routingを確認する。このTemplateはAgentCanonのsource/runtimeを実行依存に
しないが、Codexの作業規約はstandalone AgentCanonの正本に従う。

This repository owns the generated project's source, Docker dependency example,
documentation, and local policy. External tool and runtime repositories are
not part of this checkout.

## Working boundary

- Make repository changes only beneath this repository root. Generated build,
  test, and report artifacts must use the tracked project-owned paths or the
  ignored `workspace/` area.
- The Dockerfile is an example input and must not become a hidden bootstrap or
  validation requirement for derived projects.

## Completion

Before delivery, inspect the exact diff and preserve the project source and
dependency-template boundaries.
