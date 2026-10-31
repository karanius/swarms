# Layer construction: explicit contracts before promotion

This is Study E's proposed ontology and controller, not an upstream Langflow guarantee or evidence of learned emergence. Configuration is a supporting plane of bindings/settings; the containment order is Components → Composite → Flows → Processes. A view can display these as planes while the authoritative object remains one identity-preserving instance document.

## Plane contracts

| Plane | Unit and identity | Defining content | Static acceptance gate | Evidence still required |
|---|---|---|---|---|
| Configuration | Scoped binding occurrence linked to native node and field | Typed setting or external resource reference, provenance, unknown/conflicting status | Target/field exists; type and conditional requirements considered; no secret values; unsupported settings remain explicit | Provider availability, active dynamic fields, runtime validity |
| Components | Native occurrence referencing a pinned definition | Native inputs/outputs, configuration references, origin, role separate from type | Actual builder-generated identity, field/port evidence and reference integrity | Whether configured component performs its role |
| Composite | A bounded capability occurrence | Nonempty component membership, induced internal wiring, boundary exports, purpose contract and retained obligations | Members exist at immediate lower plane; every crossing relation exposed; required lower obligations inherited | Purpose, useful boundary, actual behavior |
| Flows | Coordination occurrence | Composite occurrences, handoffs, ordering/branch guards, termination, failure/retry policy | All handoffs reference exposed lower interfaces; explicit coordination contract; unresolved control realization retained | Scheduler, guards, termination and recovery execution |
| Processes | Accountable outcome occurrence | Flow occurrences, role/resource references, lifecycle, policy/approval and completion evidence | Outcome and owner defined or explicitly unknown; roles/decisions realized below or recorded as obligations | Human authority, policy approval and outcome attainment |

## Different edges carry different claims

Containment answers “what belongs inside”; wiring answers “where data moves”; control answers “when another step may run”; binding answers “what resource supplies a field”; realization answers “what lower evidence supports a higher claim”; evidence links answer “where did this assertion come from.” They are not interchangeable. A wire between two agents cannot implement human approval. A cluster cannot establish a capability. A source file called a flow cannot establish our Flows-plane contract.

## Finite proposed controller

State is S=(I,R,L,O,E,H): intent, requirements, layered instance, open obligations, evidence, revision history. Each requirement keeps one immutable ID. Each occurrence keeps a stable ID across revisions except an explicit rename with a complete reference update. Definitions and occurrences are distinct. Every operation records precondition, patch, witness and revision parent.

1. Normalize intent into explicit requirements; uncertain interpretation creates a question, not an invented policy.
2. Propose a process/outcome boundary and accountable roles.
3. Decompose into flow obligations, then capability/composite obligations, then native component/configuration needs. These proposals do not become supported merely by being written.
4. Search the pinned library, using mined patterns only as ranking hints. Select native components and build a private graph through native Langflow functions.
5. Derive composite boundaries from those same occurrence IDs. Expose crossing wires and unresolved configuration dependencies.
6. Check flow handoffs/control requirements, then process outcomes/roles/policies. Promote only the evidence tier actually checked.
7. If a gate fails, revise the smallest affected region, retain unrelated state, or ask a targeted question. A missing lower witness invalidates the dependent upper claim.
8. Stop on supported scope, an explicit question/rejection, unchanged state, repeated state, or a finite work budget. A stop is not automatically success.

For member set M and native wire set W, internal wires are W[M]={e∈W : source(e)∈M and target(e)∈M}. The boundary cut is ∂M={e∈W : exactly one endpoint lies in M}. Every edge in ∂M requires an exposure witness. The verifier checks exact equality, not merely that listed exposures are plausible. Required fields without an internal supplier or admissible binding must become explicit external inputs or open obligations. Parent readiness cannot exceed its weakest mandatory dependency.

No scalar progress score is assumed to monotonically improve: discovering an obligation may increase the open count while increasing honesty. Progress is a new justified witness, a resolved conflict, a preserved requirement through revision, or a precise actionable question. Unknowns cannot be subtracted from a denominator to inflate completion.

## One initial realization and its boundary

A static ticket-triage draft/review graph is an authored demonstration. Two native Agent occurrences may implement distinct proposed draft/review roles, with ChatInput/ChatOutput at the boundary. The model resources, approved triage policy, actual human approval mechanism and behavior evidence remain open. Agent review is not human approval. Composite/flow/process packaging is a proposed interpretation over the native graph, checked for structural fidelity only.

## Research basis

See `layer-builder-research.md` for primary local source citations and `layer-external-sources.md` for official upstream documentation. Native builder functions assemble component graphs; upper-plane contracts and promotion gates are our explicit theory. Study C's negative mining comparison remains unchanged; this construction study does not show that mining improves the builder.
