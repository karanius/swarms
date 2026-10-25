---
schema_version: 1
id: instance-machine/canonical-specification
title: Canonical Specification
type: architecture-placeholder
status: to-define
created: 2026-10-25
updated: 2026-10-25
tags: [instance-machine, architecture]
related:
  - instance-machine/domain-model
  - instance-machine/contracts
  - instance-machine/compiler-lifecycle
---

# Canonical Specification

Define the authoritative instance record shared by planning, documents, the canvas, and execution.

## Define together

- [ ] Identity, revision, intent, scope, and ownership of an instance.
- [ ] Requirements and acceptance criteria with stable identifiers.
- [ ] Confirmed decisions, assumptions, proposals, and open questions.
- [ ] Decomposition, contracts, selected definitions, versions, and configuration.
- [ ] Connections and traceability between parent requirements and child assemblies.
- [ ] References to executable artifacts, runs, and evidence.
- [ ] Authoritative fields versus derived views and generated documents.
- [ ] Storage format, schema evolution, editing, conflict handling, and history.

## Record outline template

- Instance identity and revision:
- Intent and scope:
- Requirements and constraints:
- Decisions / assumptions / unknowns:
- Decomposition and assembly references:
- Versioned dependencies and configuration references:
- Acceptance criteria and evidence references:
- Change provenance:

This is an outline to define, not a finalized executable schema. The serialization format and authority boundaries remain open decisions.

## First questions

1. What is authoritative, and which representations are generated from it?
2. How does an accepted conversational change become a new revision?
3. What happens when a canvas edit conflicts with the current specification?

## Implementation that follows

A versioned instance schema and storage API, plus document and canvas projections. Credentials should be referenced through their configured storage rather than copied into knowledge records.

## Definition gate

- [ ] One instance can be represented without conflicting sources of truth.
- [ ] A requirement can be traced through decomposition to its verification evidence.
- [ ] Save, reopen, and revision behavior are specified.

## Working decisions

No decisions have been recorded in this placeholder yet. Add a dated entry with its status, rationale, and source when we resolve a question.

## Related records

- [Domain Model](domain-model.md)
- [Contracts](contracts.md)
- [Compiler Lifecycle](compiler-lifecycle.md)
- [Knowledge index](README.md)
