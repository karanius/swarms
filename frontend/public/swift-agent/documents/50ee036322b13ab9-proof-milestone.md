---
schema_version: 1
id: instance-machine/proof-milestone
title: Proof Milestone
type: architecture-placeholder
status: to-define
created: 2026-10-25
updated: 2026-10-25
tags: [instance-machine, architecture]
related:
  - instance-machine/domain-model
  - instance-machine/contracts
  - instance-machine/canonical-specification
  - instance-machine/compiler-lifecycle
---

# Proof Milestone

Specify the end-to-end demonstration that will establish the first useful implementation.

## Choose together

- [ ] One bounded use case and its intended highest composition layer.
- [ ] Supplied input data and expected observable outcomes.
- [ ] Available primitives and permitted external effects.
- [ ] At least one composite that must be reused in a second assembly.
- [ ] Runtime, quality, cost, and manual-intervention acceptance limits.

The existing support-ticket triage example is a candidate, not a selected proof case. Prior demonstrations establish bounded flow execution; they do not establish the complete instance compiler.

## Acceptance scenario template

- Given:
- User intent:
- Expected structured specification:
- Expected decomposition and reusable boundaries:
- Expected executable behavior:
- Expected failure or gap behavior:
- Saved artifacts and version references:
- Reopen and reuse procedure:
- Evidence required:

## End-to-end acceptance checklist

- [ ] Capture intent and produce a validated structured specification.
- [ ] Decompose requirements to available components or report explicit gaps.
- [ ] Assemble and test a composite, then use it in a working flow.
- [ ] Trace results back to the original acceptance criteria.
- [ ] Save the specification, assembly, versions, and evidence.
- [ ] Reopen the instance with equivalent configuration and behavior.
- [ ] Reuse the saved composite in a second assembly.
- [ ] Demonstrate rejection of an incompatible connection and an unsupported requirement.
- [ ] Expose a real execution failure without marking it passed.

## Implementation that follows

A repeatable end-to-end test suite, fixtures, and an evidence report. Pass/fail outcomes stay empty until the relevant checks actually run.

## First questions

1. Which single use case best tests the whole mechanism?
2. What makes the second use case a meaningful reuse test?
3. What exact evidence would convince us this milestone is achieved?

## Working decisions

No decisions have been recorded in this placeholder yet. Add a dated entry with its status, rationale, and source when we resolve a question.

## Related records

- [Domain Model](domain-model.md)
- [Contracts](contracts.md)
- [Canonical Specification](canonical-specification.md)
- [Compiler Lifecycle](compiler-lifecycle.md)
- [Knowledge index](README.md)
