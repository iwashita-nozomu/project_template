# C++ build layout

<!--
@dependency-start
contract design
responsibility Documents the parent-owned C++ project and CTest build boundary.
downstream implementation ../../cpp/CMakeLists.txt single C++ project entrypoint
downstream design ../../cpp/README.md language-local layout
@dependency-end
-->

`cpp/` is the parent repository's only CMake project root. The parent owns the
source inventory, CTest graph, native experiment targets, install tree, and all
build artifacts. AgentCanon is not a build dependency and is not read by CMake.

```bash
cmake -S cpp -B build/cpp/dev \
  -DCMAKE_INSTALL_PREFIX="$PWD/.state/cpp-install/dev"
cmake --build build/cpp/dev --parallel
ctest --test-dir build/cpp/dev --output-on-failure
```

Use out-of-source build directories under `build/cpp/<profile>/`. Do not place
generated files, compiler caches, test fixtures, or reports in the source tree.
The project container and its CI job provide C++ dependencies; the separate
AgentCanon tool container must not mount `cpp/`, `tests/`, or the CMake build
tree for project execution.
