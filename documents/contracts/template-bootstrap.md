# Template bootstrap contract

## Goal

A normal clone of `project-template` is complete for project-owned bootstrap,
build, and validation. The tracked `vendor/.gitkeep` only preserves an empty
project-owned extension directory. Unrelated project-owned vendor or submodule
choices are not prohibited by this contract.

Bootstrap changes only project identity and reader-facing examples. It is
offline and repository-local. It must not clone another project, resolve a
latest revision, read credentials, or modify a global installation.

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
bash test/testrunner.sh
```

The project bootstrap does not install language tools. The project Dockerfile
and test runner own project dependencies and test execution.
