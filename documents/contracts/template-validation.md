# Template validation contract

The repository owns two normal validation entry points:

- `bash test/testrunner.sh` runs the complete static, tooling, Docker-contract,
  and C++ list;
- `bash tools/check_fresh_clone.sh` validates an initialized ordinary
  source-free descendant clone.

Targeted CMake development uses `cmake --preset dev`,
`cmake --build --preset dev`, and `ctest --preset dev`.

Project checks do not initialize a submodule, resolve an external source root,
load host hooks, contact a secondary archive, or inspect another checkout.
Project Docker validation uses the tracked `docker/Dockerfile` and parent test
runner.

## Fresh-clone boundary

The fresh-clone check starts from a clean committed tree and validates exactly
what a user receives from an ordinary clone. It may use a temporary local bare
remote, but it does not use recursive clone options, credentials, a vendor
checkout, or root symlink projections. Docker execution is explicit and is
limited to the project image.
