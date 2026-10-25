---
schema_version: 1
id: instance-machine/contracts
title: Contracts
type: architecture-placeholder
status: to-define
created: 2026-10-25
updated: 2026-10-25
tags: [instance-machine, architecture]
related:
  - instance-machine/domain-model
  - instance-machine/canonical-specification
  - instance-machine/compiler-lifecycle
---

# Contracts

Define what an assembly promises and what must hold for it to work.

## Define together

- [ ] Input and output types, meanings, required fields, and examples.
- [ ] Preconditions, postconditions, and invariant constraints.
- [ ] Configuration, dependencies, permissions, and external effects.
- [ ] State, memory, concurrency, failures, retries, and stopping conditions.
- [ ] Version compatibility and how contracts compose across boundaries.
- [ ] Structural checks versus behavioral tests and their evidence requirements.

## Contract record template

- Capability and version:
- Inputs:
- Outputs:
- Preconditions:
- Required behavior and constraints:
- Dependencies and allowed effects:
- Failure and stopping behavior:
- Acceptance checks:
- Evidence and verification scope:
- Unresolved choices:

## First questions

1. What is the minimum contract every component and composite must expose?
2. Which compatibility checks can be enforced before execution?
3. What evidence allows us to label a particular version verified?

## Implementation that follows

Machine-readable contract schemas, compatibility validators, and acceptance tests. A structurally valid connection does not by itself prove correct behavior.

## Definition gate

- [ ] One primitive and one composite have concrete contracts.
- [ ] We can identify both a compatible connection and an invalid one.
- [ ] Success, failure, and unsupported requirements have explicit meanings.

## Working decisions

No decisions have been recorded in this placeholder yet. Add a dated entry with its status, rationale, and source when we resolve a question.

## Related records

- [Domain Model](domain-model.md)
- [Canonical Specification](canonical-specification.md)
- [Compiler Lifecycle](compiler-lifecycle.md)
- [Knowledge index](README.md)
