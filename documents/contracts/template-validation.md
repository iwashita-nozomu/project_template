# Template validation contract

## Invariants

`docker/Dockerfile` is the sole owner of the standard validation environment.
Every profile command runs in target `cpu-dev`; no workflow, Dev Container hook,
or repository script creates a virtual environment or installs a package after
container start. The image owns `/opt/project-venv`, Node.js, npm, the standard
CLIs, the native toolchain, and the non-root `project` identity.

Applicability and success are different dimensions. An independent profile is
reported as `not_applicable`; it is never represented as a passing check. The
single required GitHub check is `Validation Summary`, whose JSON and Markdown
evidence retain every profile and one of these states:

- `applicable` + `pass`
- `applicable` + `fail`
- `not_applicable`

## Canonical responsibility projection

The only path-to-command mapping is `validation/profiles.toml`. Let `P` be the
ordered profile set, `C` the changed path set, and `M(f) ⊆ P` the profiles whose
tracked glob matches path `f`. For an ordinary pull request, the selected set is

```text
S(C) = union(M(f) for f in C)
```

with three conservative overrides:

1. A path not covered by any mapping is assigned to `base-project`.
2. A change to the routing authority (`validation/profiles.toml`, the router,
   its regression test, the workflow projection, this contract, or the
   Makefile command surface) selects all profiles.
3. `push` and `workflow_dispatch` select all profiles independent of paths.

The router is `tools/validation_routing.py`. It emits
`.state/validation-plan.json`, executes only applicable commands, and writes
`.state/validation-result.json`. GitHub Actions only builds/runs the canonical
image and projects router outputs; it does not duplicate path lists or profile
commands in YAML.

## Profiles

| Profile | Owned responsibility | Canonical command |
| --- | --- | --- |
| `docs` | Markdown and local-link integrity | `make docs-check-local` |
| `base-project` | self-containment, lint, typing, package build, and tooling tests | `make base-project-check-local` |
| `cpp` | CMake configure/build/install boundary and CTest | `make cpp-test-local` |
| `github-automation` | workflow structure and canonical-image projection | `make github-workflow-check-local` |
| `docker-runtime` | Dockerfile, locks, Dev Container projection, and environment ownership | `make docker-contract-check-local` |
| `bootstrap` | initialized descendant and real normal-clone lifecycle | `make fresh-clone-check-local` |

Typical pull-request routing is therefore:

| Change | Applicable profiles |
| --- | --- |
| documentation only | `docs` |
| C++ only | `cpp` |
| workflow only | `github-automation` |
| bootstrap script or bootstrap contract | `bootstrap` |
| documentation plus C++ | `docs`, `cpp` |
| unclassified file | `base-project` |
| routing authority | all profiles |

A `docker-runtime` change also triggers
`docker/cold-build-smoke.sh --pull --no-cache`. That builds target
`cpu-validation`, copies the committed source into the image, constructs a
synthetic local Git commit, runs the full local profile set, and then performs
an image-only smoke. The broad check is justified because a Dockerfile change
can alter every profile's execution semantics.

## Local commands

Inside target `cpu-dev` or the Dev Container:

```bash
make check-matrix
make pr-check
make fresh-clone-check
```

`make pr-check` is the full local confidence set. Pull-request CI may select a
strict subset through the canonical router. `make fresh-clone-check` requires a
clean committed tree and publishes the initialized descendant to a temporary
local bare remote before cloning it normally. The descendant reuses the
already-built image capabilities and runs `make validation-core-local`; it does
not install dependencies or build a nested image.
