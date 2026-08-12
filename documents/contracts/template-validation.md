# Template Validation Ownership

This document is the canonical rationale owner for validation mechanisms that belong to the Template repository itself. Shared AgentCanon validation policy remains owned by AgentCanon and is referenced rather than copied here.

## Pull-request baseline

Ordinary Template pull requests run `make pr-check`, which validates the Template-owned documentation, GitHub workflow configuration, and native C++ surface. It intentionally does not run AgentCanon's repository-wide full-confidence suite or the repository-machinery Python test suite for every parent-repository change. The current `python/` project surface contains no implementation beyond its placeholder; project Python checks become relevant when project Python source exists.

**Why keep:** a parent pull request still needs direct oracles for the Template-owned product and repository surfaces that currently contain implementation.

**Boundary:** this baseline is not a changed-path classifier and does not redefine AgentCanon validation responsibilities. AgentCanon source changes use the AgentCanon owner route and its own validation contract. Repository-machinery tests stay in the full integration gate rather than becoming an ordinary parent-PR tax.

## Full repository confidence

`make ci` is the broad integration gate. It runs after changes reach `main` and when explicitly requested through the CI workflow's manual dispatch path.

**Why keep:** integration can expose cross-surface failures that focused Template checks do not cover.

**Why not on every pull request:** running the complete shared AgentCanon/static/eval/container and repository-machinery surface for an ordinary parent change duplicates upstream responsibility and adds unrelated failure modes without improving the pull request's direct product oracle.

## Fresh-clone acceptance

`make fresh-clone-check` validates clone, AgentCanon checkout/materialization, bootstrap, update, and devcontainer-related lifecycle behavior. The CI workflow runs it on `main` and manual dispatch, not on every pull request.

**Why keep:** clone/bootstrap/update failures depend on repository and submodule lifecycle state that focused product tests do not reproduce.

**Why not on every pull request:** ordinary source or documentation changes do not alter the clone/bootstrap lifecycle, so replaying the full fixture for each pull request is not an additional correctness oracle for those changes.

## Docker cold-build smoke

The Docker Build workflow owns the clean image/runtime smoke for Docker and runtime inputs such as `docker/**`, `.devcontainer/**`, `.dockerignore`, and Python packaging inputs that affect the image.

**Why keep:** image construction, runtime identity, dependency installation, and bind/runtime behavior cannot be proven by native C++ or static repository checks alone.

**Boundary:** `cpp/**` by itself does not trigger a cold no-cache image build. Native C++ correctness is owned by `make cpp-test`; mixed C++ and Docker/runtime changes still trigger both the ordinary CI baseline and Docker Build because the runtime input is present.

## AgentCanon boundary

Template does not copy AgentCanon's rationale into a second parent-repository policy. Shared runtime validation, profiles, skills, and projection contracts remain owned by the pinned `vendor/agent-canon` source and its canonical documents. The Template owns only the parent integration and product/runtime mechanisms described above.
