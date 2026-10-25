---
schema_version: 1
id: instance-machine/index
title: Instance Machine Foundations
type: knowledge-index
status: defining
created: 2026-10-25
updated: 2026-10-25
tags: [instance-machine, architecture]
---

# Instance Machine Foundations

A linked workspace for defining the machine together before implementing its foundations. The five records are placeholders with questions, record templates, and definition gates. They are not approved specifications or working subsystems.

| Record | What we will define | What it will produce |
| --- | --- | --- |
| [Domain Model](domain-model.md) | Terms, boundaries, and relationships | Entity and relationship schemas |
| [Contracts](contracts.md) | Interfaces, obligations, compatibility, and evidence | Contract schemas, validators, and tests |
| [Canonical Specification](canonical-specification.md) | The authoritative instance record and its projections | Versioned schema, storage, and view interfaces |
| [Compiler Lifecycle](compiler-lifecycle.md) | States, transitions, decomposition, assembly, and recovery | Executable controller and subsystem interfaces |
| [Proof Milestone](proof-milestone.md) | One end-to-end success definition | Fixtures, acceptance tests, and evidence |

## Open knowledge conventions

- UTF-8 Markdown for human-readable content, YAML frontmatter for metadata, and relative Markdown links for navigation. These are project conventions, not a claim to implement a separate formal standard.
- Stable record IDs support future indexing. The frontmatter schema version describes these knowledge records, not the yet-to-be-defined instance schema.
- Keep open questions, proposals, confirmed decisions, and observed evidence distinct. A checked design item does not imply implemented or verified software.
- Record decisions with a date, rationale, and source. Link supporting artifacts when they exist.
- Keep this knowledge workspace readable without a particular app; version it with the project.

## How we will work together

Start with the Domain Model. Take one unresolved question at a time, work through a concrete example, and record the resulting decision in the owning document. Follow its implications into the linked records. Use the Proof Milestone to keep the design grounded; implement only when the necessary definitions and checks are concrete.

## Existing context

- [Instance Builder Sequence](../../INSTANCE-BUILDER-SEQUENCE.md)
- [Instance Compiler Algorithm](../../INSTANCE-COMPILER-ALGORITHM.md)
- [Metadata-driven Composition Workbook](../../CONCEPT.md)

The existing sequence and algorithm remain context. These placeholders refine their unresolved definitions rather than silently replacing them.
