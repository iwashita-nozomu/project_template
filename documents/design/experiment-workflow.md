# Experiment workflow

<!--
@dependency-start
contract design
responsibility Documents the parent-owned experiment registry, run, and report boundary.
downstream design ../../experiments/README.md experiment hub
@dependency-end
-->

The parent repository owns `experiments/registry.toml`, topic source, run
configuration, result artifacts, and reports. A managed experiment must record
the exact command, commit, configuration, environment (with secrets redacted),
and output paths under the topic's result directory.

AgentCanon is not an experiment runner dependency. If AgentCanon evaluates an
experiment, it is an external analysis consumer: register the parent target
explicitly, keep project tests and build state out of the AgentCanon tool
runtime, and write eval evidence to AgentCanon's external spool. Publication,
when authorized, goes to `agent-canon-log` and does not write this source tree.
