# Responsibility-based validation routing

## Problem

A monolithic pull-request gate makes every independent change pay the maximum
validation cost. Splitting the workflow into hand-maintained path-filtered jobs
would reduce cost but introduce a second mapping that can drift from local
commands. The design therefore keeps one typed mapping and treats workflow YAML
as a projection only.

## Model

Each profile is a repository responsibility with a command and path language.
The selector computes the union of responsibilities touched by a change. The
cost model is additive:

```text
cost(change) = sum(cost(profile) for profile in selected(change))
```

subject to the safety constraints documented in the validation contract:
unclassified paths fall back to the base profile, routing self-changes and
integration events select the full set, and Dockerfile changes receive a cold
full-image acceptance because they can change every command's semantics.

This model is monotone: adding a changed path cannot remove a previously
selected profile. It is also fail-closed at the two uncertainty boundaries
(unclassified files and classifier changes).

## Evidence

The plan records changed paths, matched paths, reason, command, and
applicability for every profile. The result records applicability, execution
result, return code, and duration. Profiles not selected by the plan are never
executed, and their final state remains `not_applicable` even if a hypothetical
outcome map contains a failure.

Regression fixtures cover documentation-only, C++-only, workflow-only,
bootstrap, multi-responsibility, unknown-path, self-change, and full-event
cases. They also prove that a non-applicable failure cannot fail the aggregate.
