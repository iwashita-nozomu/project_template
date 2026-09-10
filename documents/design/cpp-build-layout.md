# C++ build layout

<!--
@dependency-start
contract design
responsibility Defines reusable library, dependency, experiment, and validation CMake ownership.
downstream implementation ../../CMakeLists.txt library entrypoint
downstream implementation ../../include/project/version.hpp public interface
downstream implementation ../../src/version.cpp production implementation
downstream implementation ../../test/cpp/version/CMakeLists.txt standalone validation project
@dependency-end
-->

CMake projects are organized by purpose. The repository root builds the library
and declares its dependencies. Each C++ experiment or validation case has its
own `CMakeLists.txt` and consumes the library target. The root builds only the
library and its dependencies; it never reads test or experiment CMake projects,
including when configured as the top-level project.

| Location | Responsibility |
| --- | --- |
| `CMakeLists.txt` | Library targets, their dependencies, and install rules |
| `experiments/<topic>/CMakeLists.txt` | Experiment executable and experiment-only dependencies |
| `test/cpp/<case>/CMakeLists.txt` | Standalone validation executable and case-only dependencies |

## Dependency and consumer policy

Declare library dependencies in the root CMake project with
`FetchContent_Declare()` and `FetchContent_MakeAvailable()`. Pin Git sources to
full commit SHAs and link dependency targets to `project-core` with the
appropriate `PUBLIC` or `PRIVATE` scope. The root contains a commented
placeholder example; no external library is fetched by the template.

Consumers add the library with `FetchContent_MakeAvailable()` or
`add_subdirectory()` and link `project::core`. Use a separate binary directory
when adding a source directory outside the consumer. Do not `include()` the
root `CMakeLists.txt`: it is a project entrypoint, not an include module.
Experiments and validation cases declare only their own extra dependencies;
they do not repeat the library's dependency declarations.

The library requires C++20 through its target usage requirements. When embedded,
it does not change the consumer's global language standard, output directories,
or compilation database settings. Its install rules remain available to
consumers. Root-only convenience settings are guarded by `PROJECT_IS_TOP_LEVEL`.
CTest setup belongs to validation projects, not the root library.

## Build and validate

From the repository root, build and install the library:

```bash
cmake -S . -B workspace/build/project
cmake --build workspace/build/project --parallel
cmake --install workspace/build/project --prefix "$PWD/workspace/install"
```

Build the concrete version validation project independently:

```bash
cmake -S test/cpp/version -B workspace/build/version
cmake --build workspace/build/version --parallel
ctest --test-dir workspace/build/version --output-on-failure
```

The version case adds the root library only when `project::core` is absent;
it can also reuse a target supplied by a consuming project. Dependency flow is
one way: validation and experiment projects consume the library, and the
library does not discover or include those projects.

Public headers remain in `include/`, library sources in `src/`, concrete
experiments in `experiments/`, and validation cases in `test/cpp/`. Generated
build and install output belongs in ignored paths such as `workspace/`.
Docker is an optional dependency example. See the
[experiment workflow](experiment-workflow.md) and
[C++ validation guide](../../test/cpp/README.md).
