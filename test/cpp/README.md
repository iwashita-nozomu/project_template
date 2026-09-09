# C++ tests

`version_test.cpp` is the concrete CTest smoke test for the root
`project::core` library. The current `CMakeLists.txt` is included by the product
root through `add_subdirectory()` and relies on that target; configure this
sample from the repository root.

Keep C++ test build definitions alongside their sources. Register tests in
`test/cpp/CMakeLists.txt`, or give a concrete case its own
`test/cpp/<case>/CMakeLists.txt`. A case may be included through
`add_subdirectory()` or define an independent project when it needs a separate
configure entrypoint. Independent projects define their CMake minimum version,
`project()`, dependencies, and CTest setup, and document their exact commands in
the case README. Keep separate build output under an ignored location such as
`workspace/build/test/<case>/`.

See the [C++ build layout](../../documents/design/cpp-build-layout.md) for the
product, dependency, experiment, and test project boundaries.
