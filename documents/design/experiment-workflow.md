# Experiment workflow
<!--
@dependency-start
contract design
responsibility Defines one parent-owned experiment source, result, and report boundary.
downstream design ../../experiments/README.md experiment placement guide
@dependency-end
-->

The parent repository owns topic source, run configuration, result artifacts,
and reports below one root `experiments/` tree. The template defines placement,
not a generic runner or registry.

Each concrete topic documents its exact command, source revision,
configuration, relevant environment identity, output paths, and cleanup. A
C++ topic owns its source and `experiments/<topic>/CMakeLists.txt`. That build
configuration may define an independent CMake project or be included through
`add_subdirectory()`; it can also consume product libraries or executables.
Independent projects document their own configure entrypoint and build directory.
This does not create a second experiment lifecycle beneath `src/`, `test/`, or
another language directory.

External analysis tools are not experiment-runner dependencies. Project
execution and results remain parent-owned.

A C++ experiment consumes `project::core` through `FetchContent` or
`add_subdirectory()`. Library dependencies are declared by the root library;
the experiment declares only experiment-specific dependencies in its own
`CMakeLists.txt`. Pin Git dependencies to full commit SHAs. Do not `include()`
the root library's `CMakeLists.txt`.
