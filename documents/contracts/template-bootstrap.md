# Template bootstrap contract

## Goal

A normal clone of `project-template` is complete for project-owned bootstrap,
build, and validation. AgentCanon is deliberately not part of that checkout:
there is no submodule, populated AgentCanon vendor checkout, root projection,
symlink view, or hidden source resolver. The tracked `vendor/.gitkeep` only
preserves an empty project-owned extension directory; it is not an AgentCanon
registration or runtime dependency.

Bootstrap changes only project identity and reader-facing examples. It is
offline and repository-local. It must not clone AgentCanon, initialize a
checkout, resolve a latest revision, read credentials, or modify a global Codex
installation.

## Project entry points

Preview and apply the project identity conversion as follows:

```bash
bash scripts/start_repository.sh --project-slug example \
  --display-name "Example" --dry-run
bash scripts/start_repository.sh --project-slug example \
  --display-name "Example"
```

Review and commit the result before validation:

```bash
git diff --check
git add --all
git commit -m "Initialize example"
make pr-check
```

The project bootstrap does not install language tools. The project Dockerfile
and test runner own project dependencies and test execution.

## Optional AgentCanon development

AgentCanon editing is a separate workflow. The clone and runtime must be under
the ignored project workspace, qualified by the task, and removed at closeout:

```text
workspace/agent-canondevelop/<qualified-task>/agent-canon/
workspace/agent-canon-runtime/<qualified-task>/
```

From the standalone AgentCanon checkout, use `bootstrap.sh install`, `start`,
`target add`, and (when Codex is needed) `codex prepare` / `codex launch`. The
target mode must be explicit. The AgentCanon container is a shared tool plane;
it does not own or mount the project's tests, build tree, credentials, or
Docker socket. Project tests remain parent-owned.

AgentCanon `eval collect` writes to its external runtime spool. `eval sync`
publishes through the typed adapter to the separate
[`agent-canon-log`](https://github.com/iwashita-nozomu/agent-canon-log)
repository. Archive failure preserves the spool for retry and never leaves
logs, reports, caches, or generated files in this source checkout.

## Closeout

At the end of an AgentCanon task:

1. stop the runtime and uninstall the managed installation;
2. remove only the exact task clone and runtime under `workspace/`;
3. verify `git status --short`, `git diff --check`, and the absence of runtime
   artifacts in the parent repository.

The parent bootstrap never performs these cleanup operations implicitly because
it never creates the AgentCanon resources.
