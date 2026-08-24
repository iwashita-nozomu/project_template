# Experiment reports
<!--
@dependency-start
contract design
responsibility Documents durable reader-facing reports for concrete experiment runs.
upstream design ../README.md experiment placement guidance
upstream design ../../documents/design/experiment-workflow.md report boundary
@dependency-end
-->

Store one report per concrete run and link it to
`experiments/<topic>/result/<run-name>/`.

Each report records:

- the question and comparison target;
- the exact command, source revision, and configuration;
- the result directory and relevant environment identity;
- the principal generated files and their digests;
- limitations and the next action.

Do not cite generic manifest or log names unless the topic runner actually
creates and owns them.
