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
├── <entrypoint and configuration owned by the topic>
└── result/<run-name>/
```

The topic README records the question, exact command, configuration, source
revision, and expected result files. Generated run output belongs below
`result/<run-name>/` and is ignored. A durable reader-facing report belongs in
`experiments/report/<run-name>.md`.

This template does not claim a generic experiment creator, registry, runner,
or context synchronizer. Add such a tool only with the project behavior that
needs it and document the actual command in the topic README.
