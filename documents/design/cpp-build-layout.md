# C++ build layout
<!--
@dependency-start
contract design
responsibility Defines product, dependency, experiment, and test CMake responsibilities.
downstream implementation ../../CMakeLists.txt product CMake entrypoint
downstream implementation ../../dependencies/cpp/CMakeLists.txt independent dependency entrypoint
downstream implementation ../../include/project/version.hpp public interface
downstream implementation ../../src/version.cpp production implementation
downstream implementation ../../test/cpp/CMakeLists.txt CTest consumer
@dependency-end
-->

CMake projects are organized by purpose; the repository may have multiple
project roots. The root `CMakeLists.txt` owns the sample product build, and
`dependencies/cpp/CMakeLists.txt` owns external dependency installation.
C++ experiments and tests keep their own `CMakeLists.txt` alongside their sources.

| Location | Responsibility |
| --- | --- |
| `CMakeLists.txt` | Product library and its build configuration |
| `dependencies/cpp/CMakeLists.txt` | Independent dependency installation project |
| `experiments/<topic>/CMakeLists.txt` | Build configuration for a concrete C++ experiment |
| `test/cpp/CMakeLists.txt` or `test/cpp/<case>/CMakeLists.txt` | C++ test suite or case build configuration |

A local `CMakeLists.txt` may be an independent project or be included through
`add_subdirectory()`. An independent project defines its own CMake minimum
version, `project()`, and required dependency configuration. The existing
`test/cpp/CMakeLists.txt` is included by the product root and consumes its
`project::core` target; it is not currently a standalone configure entrypoint.
Add independent experiment or test projects when concrete cases require them,
with their own build directories and documented configure commands.

The product and dependency projects do not invoke each other. The sample
product has no external C++ dependencies.

```text
.
├── CMakeLists.txt    product build entrypoint
├── dependencies/cpp/ independent dependency entrypoint
├── include/          public C++ headers
├── src/              production C++ sources
├── experiments/     experiment sources and per-topic CMake configuration
├── test/cpp/         test sources and local CMake configuration
├── build/<profile>/  ignored configure/build output
└── .state/install/   ignored local install output
```

See [dependency usage](../../dependencies/README.md) for the empty dependency
entrypoint, library addition guidance, and passing an installed prefix through
`CMAKE_PREFIX_PATH` to the product build. Docker is optional for both projects.

There is no `cpp/` product wrapper and no language-local experiment tree. Concrete
experiments live below root `experiments/` and own their experiment source and
build configuration. They may also consume product libraries or executables.
See the [experiment workflow](experiment-workflow.md) and
[C++ test guide](../../test/cpp/README.md) for local entrypoint responsibilities.

Derived projects may choose a route such as:

```bash
cmake -S . -B build -G Ninja
cmake --build build --parallel
ctest --test-dir build
cmake --install build
```

The template carries one real library source and one CTest executable so a
green C++ check cannot mean “zero tests discovered.” Derived projects replace
or extend these files in the same owning directories.
