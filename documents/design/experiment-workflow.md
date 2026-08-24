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
language-specific build may produce an executable used by a topic, but it does
not create a second experiment lifecycle beneath `src/`, `test/`, or another
language directory.

External analysis tools are not experiment-runner dependencies. Project
execution and results remain parent-owned.
