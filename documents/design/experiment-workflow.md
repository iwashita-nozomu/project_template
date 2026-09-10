# Experiment workflow
<!--
@dependency-start
contract design
responsibility Defines experiment branch ownership, placement, and report boundaries.
downstream design ../../experiments/README.md experiment placement guide
@dependency-end
-->

The parent repository owns topic source, run configuration, result artifacts,
and reports below one root `experiments/` tree. The template defines placement,
not a generic runner or registry.

## Branch ownership

`main` carries shared experiment guidance. Develop and retain each topic's
source, `CMakeLists.txt`, configuration, and topic README on its experiment
branch under `experiments/<topic>/`; do not merge that experiment code into
`main` or merge the experiment branch wholesale.

Promote reusable product improvements through a separate change based on
`main`, extracting only the product changes and their relevant validation.
Keep experiment-specific code out of that change. Preserve the experiment
branch and its history after promotion; integrating a product improvement
does not make its experiment branch disposable.

Durable reports are handled separately from experiment code. A report intended
for `main` is a separate documentation change identifying the experiment
branch, exact commit, and result location; it does not bring the topic's code
into `main`. See the [report guide](../../experiments/report/README.md).

## Topic layout and execution

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
