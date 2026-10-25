---
schema_version: 1
id: instance-machine/compiler-lifecycle
title: Compiler Lifecycle
type: architecture-placeholder
status: to-define
created: 2026-10-25
updated: 2026-10-25
tags: [instance-machine, architecture]
related:
  - instance-machine/domain-model
  - instance-machine/contracts
  - instance-machine/canonical-specification
  - instance-machine/proof-milestone
---

# Compiler Lifecycle

Define the executable procedure that decomposes requirements downward and assembles verified capabilities upward.

## Starting point

The saved sequence and compiler algorithm describe the intended direction. This document will turn that direction into explicit states, transitions, interfaces, and recovery behavior. It is not an implemented controller.

## Define together

- [ ] Entry conditions and required records for each stage.
- [ ] Translation of conversation into a proposed structured specification.
- [ ] Approval and revision rules for proposed changes.
- [ ] Library resolution and recursive decomposition into child contracts.
- [ ] Missing capability handling and bounded implementation work.
- [ ] Upward assembly, structural validation, execution, and evaluation.
- [ ] Packaging, registration, versioning, and reuse of successful assemblies.
- [ ] Budgets, pauses, cancellations, failures, repairs, and restart behavior.
- [ ] Runtime events that make actual progress visible in the UI.

## Transition template

- From state:
- Trigger and required inputs:
- Operation and responsible subsystem:
- Preconditions and checks:
- Produced records and events:
- Success state:
- Failure / blocked / cancelled state:
- Retry budget and resume behavior:

## First questions

1. Which decisions belong to the model, and which are deterministic software checks?
2. What must be true before an assembly may execute or enter the reusable library?
3. How do we resume safely without repeating completed external effects?

## Implementation that follows

An executable controller, planner/tool interfaces, registry integration, a Langflow adapter, evaluator, and event log. Pi as proposer and Langflow as executor are proposed roles to refine here.

## Definition gate

- [ ] A concrete instance can be walked through every transition.
- [ ] Every transition has observable inputs, outputs, and failure behavior.
- [ ] Missing capabilities and exhausted budgets cannot silently become success.

## Working decisions

No decisions have been recorded in this placeholder yet. Add a dated entry with its status, rationale, and source when we resolve a question.

## Related records

- [Domain Model](domain-model.md)
- [Contracts](contracts.md)
- [Canonical Specification](canonical-specification.md)
- [Proof Milestone](proof-milestone.md)
- [Knowledge index](README.md)
