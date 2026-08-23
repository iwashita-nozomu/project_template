# C++ build layout
<!--
@dependency-start
contract design
responsibility Defines the root CMake project, source, test, build, and install paths.
downstream implementation ../../CMakeLists.txt root CMake entrypoint
downstream implementation ../../include/project/version.hpp public interface
downstream implementation ../../src/version.cpp production implementation
downstream implementation ../../test/cpp/CMakeLists.txt CTest consumer
@dependency-end
-->

The repository root is the only CMake project root.

```text
.
├── CMakeLists.txt
├── include/          public C++ headers
├── src/              production C++ sources
├── test/cpp/         CTest sources
├── build/<profile>/  ignored configure/build output
└── .state/install/   ignored local install output
```

There is no `cpp/` wrapper and no language-local experiment tree. Concrete
experiments live below root `experiments/` and may invoke a built executable
without taking ownership of its source or build graph.

The standard route is:

```bash
cmake -S . -B build/dev -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_INSTALL_PREFIX=.state/install/dev
cmake --build build/dev --parallel
ctest --test-dir build/dev --output-on-failure
cmake --install build/dev
```

The template carries one real library source and one CTest executable so a
green C++ check cannot mean “zero tests discovered.” Derived projects replace
or extend these files in the same owning directories.
