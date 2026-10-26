---
schema_version: 1
id: instance-machine/canonical-specification
title: Canonical Specification
type: architecture-specification
status: draft
created: 2026-10-25
updated: 2026-10-26
tags: [instance-machine, architecture, specification]
related:
  - instance-machine/domain-model
  - instance-machine/contracts
  - instance-machine/compiler-lifecycle
---

# Canonical Specification

The machine uses two related JSON records: **Library JSON** defines reusable pieces; **Instance JSON** describes the purposeful selection and assembly of those pieces for an intent. The canvas and agents edit these records through the same revision and validation procedure.

**Status:** the two-record direction is accepted in conversation. The field names, examples, editing procedure, and rules below are a concrete design proposal, ready for joint review. They do not implement a registry, compiler, storage API, or canvas synchronization. Contract details remain owned by [Contracts](contracts.md); execution procedures remain owned by [Compiler Lifecycle](compiler-lifecycle.md).

## 1. What is authoritative

| Record | Owns | Does not establish |
| --- | --- | --- |
| Library JSON | Layer definitions and exact revisions of reusable items, capability boundaries, contracts, dependency references, and internal assembly definitions | That every catalog entry is implemented, available, or behaviorally validated |
| Instance JSON | Intent, requirements, selected item revisions, instance-specific configuration and assemblies, unresolved boundaries, decisions, and evidence references | That a structurally valid design can execute or satisfies its intent |
| Supporting artifacts | Pinned native definitions, executable exports, test records, and evidence addressed by references | A competing editable copy of the design |
| Canvas/document projections | Layout and readable views of the records | Independent authority over capabilities or relationships |

JSON is the serialization format. A schema checks shape; semantic validators check relationships; behavioral checks supply evidence. None substitutes for the others.

A conversation produces proposed edits. Accepted changes produce a new revision of the owning record. Generated prose must distinguish accepted facts, proposals, assumptions, and unknowns rather than flatten them into one narrative.

## 2. Library JSON

The library is a catalog organized as **library → layers → items**. The logical record may later be stored across indexed files or a database; it does not require loading the whole library for every request.

### Proposed envelope

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Version of the JSON format, separate from content revisions |
| `kind` | `library` |
| `id`, `revision` | Stable library identity and exact catalog checkpoint |
| `layers` | Stable layer IDs, labels, and ordering; ordering alone supplies no execution semantics |
| `items` | Versioned item definitions, each assigned to a layer |

### Proposed item definition

- `id`, `revision`, `name`, `layerId`: identity and placement. References use identity and revision, never the display name alone.
- `capability`: what the item offers and its explicit limits.
- `contract`: exposed inputs and outputs, configuration obligations, and behavioral obligations. Draft port descriptions must not be mistaken for complete native type definitions.
- `definition`: either a pinned native-definition reference or an internal assembly with child references, connections, and boundary mappings.
- `dependencies`: the exact item revisions and resource bindings required by the definition. The contained child references and resource bindings must agree with this dependency inventory.
- `lifecycle`: separate design readiness, implementation, design validation, and behavior validation. Current runtime readiness is a scoped observation, not a permanent reusable property.
- `provenance`: origin and applicable licensing/attribution references for imported pieces. Public availability does not itself establish reuse permission.

A reusable assembly is a definition, not a running instance. It contains no instance's chat history, private data, or active execution state. Native artifacts and nested assemblies must resolve transitively; an empty or fabricated artifact reference cannot establish build readiness.

### Configuration below Components

Include Configuration as the organizational layer defined in the Domain Model. Reference existing Langflow provider, variable, and component-setting mechanisms. Do not introduce a parallel credential store. Library definitions declare resource needs; an instance binds them to permitted existing configuration references.

Credentials themselves stay in Langflow's configured credential storage. JSON carries references, never secret values. Nonsecret instance configuration is distinct from a credential reference.

## 3. Instance JSON

An instance is an intent-specific slice, not a copy of the catalog. It uses only the layers needed for its intent. It can contain proposed local items when the library lacks a suitable piece.

### Proposed envelope and records

| Field | Meaning |
| --- | --- |
| `schemaVersion`, `kind` | Format version and `instance` |
| `id`, `revision`, `name` | Stable instance identity and exact design checkpoint |
| `libraryRef` | Library identity and pinned catalog revision used to resolve selections |
| `intent` | Requester's starting description and its provenance; completeness is not assumed |
| `requirements`, `constraints` | Stable records describing required outcomes and permitted solution boundaries |
| `decisions`, `assumptions`, `unknowns`, `conflicts` | Separate discovery records linked to the affected design |
| `localItems` | Proposed instance-owned definitions that are not yet reusable library items |
| `assemblies` | Versioned arrangements at the layers actually used |
| `gaps` | Missing understanding, capability, configuration, connections, or evidence and the affected action |
| `evidenceRefs` | References identifying checked subjects/revisions, observed conditions, and result records |
| `provenance` | Record origin and the change/decision history references |

### Selections and connections

Each assembly owns placements with stable placement IDs. Each placement selects **either** a pinned library item reference **or** a pinned local-item reference, then adds instance-specific configuration and resource bindings. Two placements of the same definition have different placement identities and isolated state unless sharing is explicitly defined.

A connection names source placement/output and destination placement/input. It describes horizontal interaction. Native connection types and handle definitions must resolve through the Langflow adapter; the machine must not invent a simplified replacement for their actual compatibility rules.

### Decomposition and composition are different relationships

- Requirements may link to more detailed child requirements. This records why lower-level behavior is needed.
- Assemblies may claim to address identified requirements. A claim is not evidence of satisfaction.
- A proposed or reusable higher-layer item names the lower assembly that realizes it. Its boundary mappings connect each exposed port to identified internal ports.
- Layer membership alone does not supply any of these links.

The requirement and composition graphs can evolve independently while retaining traceability. Design can move top down, bottom up, or through an intermediate layer. A lower assembly may be designed before its higher package is settled. Unresolved mappings stay explicit gaps.

Do not force a chain through every layer. When an assembly is packaged, placement at the next applicable layer follows the accepted horizontal/vertical distinction and an explicit responsibility boundary, rather than a node-count heuristic. Exact layer-boundary rules remain to be completed in the Domain Model.

## 4. Concrete day-zero examples

- [Library JSON example](examples/day-zero.library.json)
- [Instance JSON example](examples/day-zero.instance.json)

These are **illustrative design fixtures**, not exports of the current Langflow catalog or the browser-local Custom library. The library starts with three component descriptions; the instance proposes a local summarizer and leaves its actual native definitions and resource bindings unresolved. It demonstrates that a complete record can truthfully describe an incomplete design.

Read the instance from its requirement down to its component assembly, then back through the proposed composite's exposed boundary. The instance does not need an Enterprise or Process record to describe this capability. No successful execution or validation is asserted.

## 5. Schema and validation responsibilities

The first formal schemas should describe these envelopes and common records without pretending to finalize behavioral contract semantics.

### Structural schema rules

- Require stable identities, explicit revisions, known record kinds, and the relevant record collections.
- Require exactly one of `itemRef` and `localItemRef` on a placement.
- Require source and destination endpoints on connections and both external/internal endpoints on mappings.
- Separate authoring/discovery status from implementation and validation judgments.
- Allow explicitly incomplete designs to be saved. Do not require credentials or a full executable graph merely to record an unresolved intent.
- Version the schema and make unsupported formats fail explicitly; do not silently drop unknown data during migration.

### Semantic validation rules

These need software beyond JSON Schema:

1. IDs are unique within their stated scope; every reference resolves at its pinned revision.
2. Layer references exist. Every endpoint names an actual placement and port in the appropriate assembly.
3. A composite's boundary mappings refer to exposed ports and internal ports with compatible native contracts.
4. Composition dependencies are acyclic. A deliberate control-flow loop is different and requires explicit stopping/failure rules; it must not be rejected merely because it is a graph cycle.
5. Requirement refinement has no self-justifying cycles. Every build-target requirement has a realization or an explicit unresolved boundary.
6. Native definitions and transitive dependencies are available and pinned before a design is called buildable.
7. Configuration bindings preserve Langflow's scopes and access semantics. Secret values cannot be serialized into these records.
8. Evidence names the exact subject revision and relevant dependency/configuration conditions. A changed subject cannot inherit a passing judgment without reconsideration.
9. Claimed design readiness agrees with unresolved gaps for that action. An execution-only configuration gap need not block unrelated design work.
10. A candidate must satisfy constraints as well as requirements; a conflict is exposed rather than silently relaxed.

Schemas can reject malformed data. They cannot prove that a claim is true, detect every secret, or judge every behavioral promise. Domain policy, storage boundaries, and tests remain necessary.

## 6. Editing, checkpoints, and conflict handling

Proposed editing procedure:

1. Load the instance and the exact dependency closure from its library checkpoint.
2. A conversation, agent, document editor, or canvas produces a proposed patch against a known base revision.
3. Validate structure and references; identify affected requirements, assemblies, dependencies, and evidence. Preserve unresolved gaps rather than substituting invented pieces.
4. Apply within the user's authorized scope. Requester-owned choices requiring clarification remain proposals; routine authorized edits need no blanket confirmation gate.
5. Persist a new consistent checkpoint with its change provenance. Derived views refresh from that checkpoint.
6. If the base revision is stale, reject or explicitly reconcile the patch. Do not silently overwrite another editor's work.

Layout can be saved as a separate view record keyed to stable placement IDs. Moving a node changes presentation, not its capability or behavioral evidence. Rewiring ports or changing configuration changes the design and may invalidate affected judgments.

A checkpoint pins the exact per-assembly and item revisions used. It can remain incomplete. Successful persistence is not a passed design check.

## 7. Versioning and safe reuse

There are separate revisions for the library checkpoint, individual library items, instance-local items, layer assemblies, and the whole instance. A new catalog checkpoint does not mean all item revisions changed.

Existing instances retain their exact selections. To adopt a newer item revision, propose an upgrade, inspect contract/dependency differences, update affected assemblies, and renew applicable validation. Do not resolve a saved `itemRef` to “latest.”

Retain referenced historical definitions or expose broken resolution explicitly. Reopening an old instance must not silently substitute a newer implementation. Format migrations preserve the original record and record the migration; content upgrades are a separate operation.

Runtime runs reference the design checkpoint but store execution state separately. Current availability can change without a design revision. Reusable definitions never automatically carry prior run memory into a different instance.

## 8. From a gap to a reusable item

1. Record the requirement and the unsupported boundary.
2. Create or refine an instance-local candidate definition, its proposed contract, and realizing assembly.
3. Resolve downward to actual components and required resource references. Reuse existing items where suitable.
4. Validate the design. This establishes build readiness only within the checks performed.
5. Build and behaviorally validate the capability; retain evidence and limitations.
6. Publish a reusable item revision with pinned dependencies, boundary mappings, provenance, and bounded validation references.
7. Explicitly replace the instance-local reference with the published item revision in a new instance checkpoint.

Proposed items can be cataloged as drafts if clearly marked, but publishing their names does not make them operational. Promotion must remove instance-specific data, run identifiers, and secret values. It must retain the contract and exact dependency definition needed for independent reuse.

## 9. Canvas and Langflow integration boundary

Current source inspection shows that V2 saves Custom items as browser-local JSON containing graph snapshots. The native adapter reads and executes a dedicated Langflow flow. Higher-plane placements reference local Custom entries, but this is not yet the canonical cross-layer instance format or an executable nested-composite registry.

The proposed canonical records sit above native Langflow artifacts:

- Import stores or references a pinned native definition/export and records its origin and limits.
- The adapter translates canonical placements and assembly mappings into native Langflow graphs while preserving native component implementation and fields.
- The canvas sends semantic edits through the same revision/validation path as an agent.
- Building emits an executable artifact pinned to a design checkpoint; execution produces separate run and evidence records.
- Existing browser-local saves need an explicit, nondestructive migration. Their `design-saved` status must not become a verified badge during import.

None of these future interfaces is implemented by this document. Source checked: `frontend/prototype-canvas/v2-canvas.jsx` and `frontend/prototype-canvas/langflow-adapter/README.md`.

## 10. Open choices for joint definition

- Complete contract fields and how inherited native contracts are pinned and exposed.
- Exact readiness states, action gates, and recursive validation rules.
- Registry/storage implementation, revision-ID strategy, access scopes, and evidence retention.
- Instance-to-instance composition: the proposed fifth business instance can reference independently scoped instances, but its interface, revision, and isolation rules are not yet specified. It is not automatically another library layer.
- Executable expansion of nested composites and explicit control-flow loops.

These do not block describing the proposed record structure. They do block claiming a production-ready compiler or complete executable schema.

## Definition gate

- [x] Library definitions and instance-specific design have separate ownership.
- [x] Examples show pinned selection, local candidates, horizontal connections, vertical mappings, and explicit gaps.
- [x] Revision, editing, migration, and evidence responsibilities are described as proposals.
- [ ] Jointly review the field names and relationship representation.
- [ ] Formalize JSON Schemas and semantic validator behavior after the relevant contract decisions.
- [ ] Demonstrate save/reopen, concurrent editing, and recursive build through the actual canvas and storage.

## Working decisions

- 2026-10-26 — Accepted direction: Library JSON organizes reusable items by layer; Instance JSON selects, configures, and connects exact items for an intent. Canvas and agents should use the same authoritative design rather than independent copies. Source: the user's library-versus-instance clarification and authorization to develop this specification.
- 2026-10-26 — Proposed design: pinned revision references, explicit instance-local candidates, action-relative gaps, independent lifecycle dimensions, and a shared patch/checkpoint procedure as described above. These elaborate accepted domain principles; exact fields and enforcement await joint review.

## Related records

- [Domain Model](domain-model.md)
- [Contracts](contracts.md)
- [Compiler Lifecycle](compiler-lifecycle.md)
- [Knowledge index](README.md)
