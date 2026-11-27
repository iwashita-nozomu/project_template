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
- the exact command, experiment branch, full source commit, and configuration;
- the result directory and relevant environment identity;
- the principal generated files and their digests;
- limitations and the next action.

Do not cite generic manifest or log names unless the topic runner actually
creates and owns them.

Reports do not automatically accompany product improvements promoted to `main`.
When a report is published there, use a separate documentation change and
identify its experiment branch and exact commit so readers can locate code
that remains on that branch. Keep result locations explicit; a path alone is
not a claim that ignored run artifacts are available in the `main` checkout.
