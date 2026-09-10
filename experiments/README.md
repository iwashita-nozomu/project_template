# Experiments
<!--
@dependency-start
contract design
responsibility Documents the single project-owned experiment source and result tree.
upstream design ../documents/design/experiment-workflow.md experiment placement contract
downstream design report/README.md run report guidance
@dependency-end
-->

`experiments/` is the only experiment owner. Do not create a language-local
experiment directory such as `cpp/experiments/`.

Create one topic directory only when the project has a concrete experiment:

```text
experiments/<topic>/
├── README.md
├── CMakeLists.txt  # for a C++ experiment
├── <entrypoint and configuration owned by the topic>
└── result/<run-name>/
```

A C++ topic owns its sources and `CMakeLists.txt`. It may define an independent
CMake project or be included by another project with `add_subdirectory()`.
For an independent project, define its CMake minimum version, `project()`, and
dependency configuration, and document its configure/build commands in the
topic README. Keep build output in an ignored location such as
`workspace/build/experiments/<topic>/`. See the
[C++ build layout](../documents/design/cpp-build-layout.md).

The topic README records the question, exact command, configuration, source
revision, and expected result files. Generated run output belongs below
`result/<run-name>/` and is ignored. A durable reader-facing report belongs in
`experiments/report/<run-name>.md`.

This template does not claim a generic experiment creator, registry, runner,
or context synchronizer. Add such a tool only with the project behavior that
needs it and document the actual command in the topic README.

A C++ experiment consumes `project::core` through `FetchContent` or
`add_subdirectory()`. Library dependencies are declared by the root library;
the experiment declares only experiment-specific dependencies in its own
`CMakeLists.txt`. Pin Git dependencies to full commit SHAs. Do not `include()`
the root library's `CMakeLists.txt`.
