---
schema_version: 1
id: instance-machine/domain-model
title: Domain Model
type: architecture-placeholder
status: in-progress
created: 2026-10-25
updated: 2026-10-25
tags: [instance-machine, architecture]
related:
  - instance-machine/contracts
  - instance-machine/canonical-specification
---

# Domain Model

Establish the language and boundaries of the instance machine.

## Starting point

A primitive is a reusable piece treated as indivisible at the current composition level. A composite is assembled from other pieces and can itself be reused. The library's layer names are working classifications; the boundaries still need to be defined.

## Define together

- [ ] Definition versus configured instance.
- [ ] Component, primitive, composite, capability, flow, process, and instance.
- [ ] The purpose and boundary of each higher layer we actually need.
- [ ] Relationships: contains, requires, connects to, implements, and satisfies.
- [ ] What makes a saved assembly reusable at its own layer.
- [ ] Separate specification, executable artifact, execution run, and evidence.

## Confirmed terms

### Intent

Intent is the starting expression of what an instance should accomplish and why. It sheds initial light on the request; it is not a complete specification and does not imply that the requester has supplied or recognized everything needed.

### Discovery

Discovery is the iterative process of exploring and clarifying intent with the requester throughout design. It investigates unstated needs, challenges assumptions, surfaces contradictions, and records requirements, decisions, constraints, and unanswered questions.

Discovery and assembly develop together. Proposed assemblies can reveal further questions; answers can change requirements and assemblies. Interviewing continues as needed rather than being restricted to one initial intake. Matt Pocock-inspired interviewing and exploration skills are the intended means of guiding this process; their implementation is separate from these domain definitions.

Clarification means sufficient understanding for the next design decision, with remaining unknowns explicit. It does not mean every possible question is answered before design begins.

### Requirement

A requirement is something the instance's design must satisfy, even while how to satisfy it is still being explored. Requirements emerge and can be refined through discovery. Exploring possible ways to satisfy a requirement can uncover further questions.

For example, “I want a ticket-triage system” expresses intent; “An urgent ticket must reach the on-call team” expresses a requirement. What counts as urgent, who is on call, and what happens if delivery fails remain questions for discovery.

The requirement's metadata fields and formal representation remain open; they have not been confirmed.

### Gap


A gap is something needed to satisfy a requirement that the current design cannot yet account for. It links what is needed to what is missing: understanding, capability, a connection, or evidence.

Gaps guide development. When a gap calls for a missing capability, resolving it produces a candidate building block: describe its purpose and boundaries, design its assembly down to available components, and refine the specification until it is buildable. Building and validating that specification establishes a functional item for the instance and a reusable capability for the library. A proposed or buildable item must remain distinguishable from a built and validated item. Gaps in understanding or evidence may instead require clarification or validation rather than a new item.

### Library growth through gap resolution

Day zero begins a growing cycle: requirements reveal gaps; resolving capability gaps grows the library; the growing library helps resolve future gaps. Each resolved capability gap should leave behind a reusable capability so future instances require less invention and more composition.

For recurring needs in a reasonably stable domain, increasing reuse should reduce the amount of new construction per intent. Instances still compose across layers; reuse reduces the need to invent missing items and abstraction layers. Unfamiliar needs can require new or revised items. Discoverability, compatibility, and appropriate scope are necessary for a larger library to remain useful.

The immediate planning target is a buildable JSON specification. Functional execution and validation are subsequent stages, not implied by a completed blueprint.

### Validation

Validation determines whether an item or assembly satisfies its requirements and records the evidence supporting that judgment.

- **Design validation:** checks whether the blueprint is coherent, including required input sources, compatible connections, available dependencies, and defined checks for requirements. Passing the applicable design checks establishes readiness to build, not proven runtime behavior.
- **Behavior validation:** checks the built assembly's results against its requirements under relevant conditions, including failures. Its conclusions are bounded by the checks performed and evidence obtained.

Validation is recursive across the composition hierarchy. At each layer, constituent items must pass their applicable checks, connections and configuration must be valid, and the resulting assembly must satisfy its own requirements. Child results provide supporting evidence for the parent; they do not replace checking the parent's combined behavior.

Individually correct pieces can form an incorrect assembly. Every higher-layer assembly therefore needs checks against its own requirements. This principle applies to both design validation and behavior validation.

A failed check exposes a gap and identifies the affected requirement and assembly for refinement. Changes affecting supporting evidence require the dependent validation judgments to be reconsidered; prior passing results are not an unconditional guarantee.

### Instance

An instance is an intent-specific vertical slice of the library stack. It selects, configures, and connects only the pieces needed to satisfy that intent.

An instance spans the layers it needs; it does not have to include every layer. Its assemblies, configuration, connections, and state are specific to that instance. Different instances may reuse the same library items while keeping their instance-specific state isolated.

### Library

The library contains layers, and each layer contains items. It supplies the pieces from which intent-specific instances are composed.

### Layer

A layer is a level within the library that organizes items of a particular kind, such as components, composite components, flows, or processes. The boundaries and meanings of individual layers remain to be defined.

### Item

An item is a building block inside a library layer. Its kind comes from its layer: a component item, composite component item, flow item, process item, and so on. An instance selects and configures items across the layers needed for its intent.

“Template” is not a separate domain concept at this stage; use “item” for the general term and the layer-specific kind when more precision is needed.

### Layer assembly

A layer assembly is an instance's particular arrangement of pieces at a given layer.

### Connection

A connection describes horizontal interaction between items, including the passage of information or control. It represents how items work together, not merely a visual line. For example, Chat Input sends a message to an Agent.

### Composition

Composition is the vertical relationship between a higher-layer item and the assembly below that realizes it. It represents what the higher-layer item is built from. For example, a Summarizer composite is realized by an assembly of Chat Input → Agent → Chat Output.

This relationship includes how the higher-layer item's exposed inputs and outputs map to its internal items. The formal representation of these mappings remains to be defined.

### Assembly

An assembly is an evolving arrangement of items, their configurations, and their connections, developed to fulfill a purpose. Assembly has two directions:

- **Horizontal assembly:** connect and configure items within a layer to produce a capability.
- **Vertical assembly:** bundle that arrangement into a single item exposed at the next layer, retaining its internal structure. For example, horizontally assembled components become one composite-component item at the composite components layer.

An instance's assemblies are developed iteratively, rather than determined all at once. Design can proceed downward from intent, upward from available components, or between intermediate layers. Proposed arrangements are revised until their internal structure and higher-level purpose fit together. An assembly may contain unresolved parts before it becomes a buildable specification; its existence as a design does not imply implementation or successful execution.

### Instance composition

Instance composition is the selection, configuration, and connection of library pieces into an intent-specific vertical slice.

### Day-zero boundary

At day zero, existing components ground composition, while their required resource configuration underpins operational readiness. Missing higher-layer items remain proposed assemblies until they are developed and validated; naming an assembly does not establish that it exists or works.

### Capability

A capability describes what an item can accomplish, under what conditions, and within what limits. Its boundary includes required inputs and conditions, provided results, and known limitations. Different items or assemblies can provide the same capability through different implementations.

A requirement states what the instance needs; a capability states what an item offers; an assembly describes how items are arranged to provide it. Boundary resolution compares requirements against available capabilities. If a requirement exceeds an item's capability boundary, the gap may require different configuration, composition with other items, or a new item.

A capability description makes a claim explicit. Validation and evidence establish how well that claim holds under specific conditions; a proposed capability must remain distinguishable from demonstrated behavior.

### Boundary resolution

Boundary resolution is the capability to locate where requirements above no longer have a supported realization below, and determine the next action needed to close that gap. It directs iteration toward affected parts of the instance rather than repeatedly rebuilding the whole design.

For each unresolved boundary, identify:

- **Where:** the affected requirement, item, assembly, and layer.
- **Why:** ambiguity, missing capability, incompatibility, configuration needs, or insufficient evidence.
- **Next action:** clarify, decompose, recompose, configure, or validate. Existing suitable items may resolve a boundary through reuse.

Several unresolved boundaries may exist simultaneously. They must be tracked separately and prioritized for further work. Detection precision, prioritization rules, formal representation, and implementation remain to be defined. This concept does not establish a mathematical entropy measure or imply that the current application implements boundary resolution.

### Dependency

A dependency identifies what an item or assembly relies upon to satisfy its requirements. Composition dependencies descend through the particular lower-layer items used, not the entire lower plane. Horizontal interactions and external resources can introduce additional dependencies. Dependency tracing continues through components into their required configuration and resources.

### Configuration layer

The Configuration layer sits below Components in our library model and exposes the existing Langflow configuration mechanisms that components depend on. It must preserve those mechanisms and their behavior rather than create an independent configuration system. Its scope includes model providers, storage, databases, search, tools, and other resources as supported by the actual components and Langflow installation.

Configuration being present is distinct from a resource being usable. Components may exist while their required configuration or resource access is unresolved. These dependencies propagate into assemblies that use them.

#### Source-backed mapping — local Langflow checkout, 2026-10-25

Inspection identifies multiple existing configuration surfaces rather than a single universal resource manager:

- **Model providers:** the original model-provider modal and configuration hook load provider fields, save variables, validate credentials, and manage model activation. Reuse these mechanisms for supported model providers.
- **Global variables:** the original settings page manages Generic and Credential variables, including field-application metadata. Reuse the existing variable references and access semantics.
- **Component-specific settings:** the original parameter renderer handles individual component fields, including password fields and variable selection. Preserve settings owned by components; do not assume storage, search, or tool integrations all have a centralized provider form.

The Configuration layer is our organizational view over these existing surfaces. It is not an upstream Langflow layer or a claim that every integration shares one configuration API. The exact canvas presentation, instance-to-Langflow scope mapping, and readiness checks remain to be defined. No canvas integration or credential changes have been performed as part of this inspection.

Source locations in the inspected checkout:

- `/Users/x/projects/langflow/src/frontend/src/modals/modelProviderModal/hooks/useProviderConfiguration.ts`
- `/Users/x/projects/langflow/src/frontend/src/controllers/API/queries/models/use-get-model-providers.ts`
- `/Users/x/projects/langflow/src/frontend/src/pages/SettingsPage/pages/GlobalVariablesPage/index.tsx`
- `/Users/x/projects/langflow/src/frontend/src/components/core/parameterRenderComponent/components/inputComponent/index.tsx`

### Evidence

Evidence is the recorded basis for a validation judgment. It makes the reason for a passing, failing, or uncertain result inspectable. Validation makes the judgment; evidence supports it.

Evidence identifies what was checked, which version was checked, the conditions, and the observed result. It can support design validation (such as port compatibility), behavior validation (such as a recorded test outcome), or an assembly's satisfaction of its own requirements beyond the success of its constituent items.

Evidence has limits: a successful test supports the tested case, not every possible case. Changes to an item or its dependencies may require related evidence to be renewed. The formal evidence record remains to be defined.

### Revision

A revision identifies a particular state of a library item, a layer assembly, or an instance's design. These can evolve independently:

- **Library item revision:** a particular definition of a reusable item.
- **Layer assembly revision:** a particular arrangement and configuration within an instance's layer.
- **Instance revision:** a consistent snapshot identifying the exact assembly revisions used across its layers.

Instances reference the library items they use while preserving their own configurations and history. Updating a shared library item does not silently update existing instance designs. The model must accommodate an open-ended number of independently evolving instances; this is a modeling requirement, not a claim of unlimited runtime capacity.

### Working design and checkpoint

A working design is elastic, potentially incomplete, and continuously editable. A checkpoint identifies a consistent snapshot that can be inspected, compared, validated, or built. Checkpointing does not itself establish that the design passed validation or is ready to build.

Versioning tracks evolving relationships and their consequences, rather than merely numbering files. When a candidate change occurs within a layer, dependency relationships identify affected assemblies above or below that may need adjustment or renewed validation. Unaffected parts need not change merely because another part evolves. Evidence remains associated with the exact revisions and conditions checked.

The composite-component layer may be especially elastic because it explores arrangements of existing components. This remains a hypothesis, not a fixed domain rule. Revision identifiers, checkpoint mechanics, and dependency-impact algorithms remain to be specified.

### Contract

A contract makes explicit what an item accepts, requires, and must produce at its boundary. Our machine inherits Langflow's existing component-level structural contracts rather than recreating them: typed inputs and outputs, field definitions and configuration requirements, connection rules, and applicable execution/input validation.

Above this foundation, assembly-level behavioral contracts describe what the combined item must accomplish, under what conditions and limits, and how satisfaction is checked. Structural compatibility alone does not establish semantic compatibility or satisfaction of an intended outcome. Two ports carrying the same data type can still disagree about its meaning.

Source inspection in the local Langflow checkout confirms input definitions in `src/lfx/src/lfx/inputs/inputs.py`, output definitions in `src/lfx/src/lfx/template/field/base.py`, and frontend connection checks in `src/frontend/src/utils/reactflowUtils.ts` (`isValidConnection`). These existing checks must not be treated as universal behavioral guarantees; some input checks warn rather than reject.

The detailed representation and enforcement of assembly-level contracts remain to be developed in [Contracts](contracts.md).

### Lifecycle state

An item or assembly has a lifecycle status profile rather than a single “done” status. Track these dimensions separately:

- **Design readiness:** whether its specification is sufficiently complete to build.
- **Implementation:** whether the specified item has been built.
- **Design validation:** judgments and evidence about the blueprint's coherence and applicable structural requirements.
- **Behavior validation:** judgments and evidence about the built item's satisfaction of behavioral requirements.
- **Runtime readiness:** whether the configurations and resources required to operate are currently available and usable.

An item can be fully designed but unbuilt, built but failing behavioral checks, previously validated but unavailable, or available after changes that have not been validated. Availability does not establish correctness, and prior validation does not establish current availability.

Design and validation judgments apply to identified revisions and conditions. Runtime readiness is a current observation and can change without a design revision, for example when credentials expire. Relevant changes require reconsideration of affected judgments and evidence. Boundary resolution uses this profile to distinguish design work, implementation work, validation work, and restoration of readiness.

Exact state names, transition rules, and the formal status representation remain open.

### Decision

A decision is a choice made during discovery or design, together with its rationale and affected parts of the instance. AI proposals remain distinct from confirmed decisions and unresolved questions.

Decisions form a linked history, represented conceptually as a graph rather than only a chronological chain:

- **Backward links:** the intent, requirements, questions, or evidence motivating the choice.
- **Forward links:** the items, configurations, and assemblies affected by it.
- **Revision links:** earlier decisions it revises or replaces, preserving their history.

This supports auditing why something exists, who confirmed a choice, and what must be reconsidered when that choice changes. The formal decision record, confirmation mechanism, and graph representation remain to be defined.

### Assumption

An assumption is a claim provisionally treated as true during exploration but not yet confirmed by sufficient evidence and validation. It is distinct from a decision, which records a choice. Approval to explore an assumption does not establish its truth.

Assumptions must remain explicit and linked to the requirements, decisions, items, and assemblies that rely on them. Their records need to identify the claim, how it can be checked, and what must be reconsidered if it proves wrong. Exact fields remain to be defined.

Hypothetical designs may depend on assumptions during exploration. An assumption alone cannot authorize consequential behavior. Before the affected construction or operation proceeds, assumptions material to correctness, permissions, cost, or required outcomes must be resolved through evidence and applicable validation. Boundary resolution marks the affected work as blocked when those prerequisites remain unresolved; unrelated exploration may continue.

Confirmation of a choice and validation of a claim are different judgments. The evidence needed to resolve a claim depends on its scope and consequences, and validation conclusions remain bounded by that evidence.

### Constraint

A constraint is a condition that limits which designs are acceptable: a boundary on the solution space. Requirements describe what must be satisfied; constraints restrict the ways it can be satisfied. For example, classifying tickets is a required outcome, while keeping customer data on the local machine restricts acceptable implementations.

Boundary resolution must consider both requirements and constraints. A candidate that achieves an outcome but violates a constraint is not an acceptable solution. When no suitable assembly can satisfy both, expose the conflict rather than silently relaxing the constraint. Constraint representation and change procedures remain to be defined.

### Conflict

A conflict exists when requirements, constraints, decisions, or available capabilities cannot fit together as currently defined. A gap identifies something missing; a conflict identifies incompatible conditions. The two can coexist.

The machine must identify the conflicting conditions, affected design, and what would need to change to resolve the incompatibility. It must not silently choose between them or relax an accepted condition. Resolution must be explicit and traceable through the decision history. Formal conflict records and resolution procedures remain to be defined.

### Unknown

An unknown is information or a decision that has not been resolved. Record it explicitly and link it to the affected requirement or assembly rather than silently filling it with an assumption.

Blocking is relative to a particular action:

- **Blocking unknown:** prevents the specified next action from proceeding responsibly.
- **Nonblocking unknown:** can remain explicit while the specified action or independent work proceeds.

For example, missing credentials may block execution without blocking blueprint design. An unknown is not globally blocking simply because it remains unanswered.

Discovery can expose unknowns by examining triggers, required information, expected results, failure behavior, and success checks. Some omissions emerge only during design or testing. Boundary resolution determines which unknowns matter for the next action. Structural omissions can be checked, factual unknowns investigated, and requester-owned choices clarified with the requester. The system does not assume it can detect every missing detail from the initial intent.

## Term record template

- Term:
- Meaning:
- Includes / excludes:
- Example / counterexample:
- Relationships:
- Decision status: open / proposed / confirmed
- Source or rationale:

## First questions

1. What exactly distinguishes a flow from a process in our system?
2. Which properties are common to every reusable assembly?
3. Do layer names change execution semantics, or organize assemblies?

## Implementation that follows

Entity schemas, stable identifiers, relationship definitions, and terminology used by the registry and UI. These have not been specified or implemented by this placeholder.

## Definition gate

- [ ] We can classify one concrete example without contradictory definitions.
- [ ] The same vocabulary can describe both primitive pieces and nested assemblies.

## Working decisions

- 2026-10-25 — Confirmed by the user: unknowns remain explicit and linked to affected designs; blocking is relative to a particular action, allowing independent work to continue. Discovery progressively exposes uncertainty rather than presuming completeness from initial intent. Source: the missing-details discussion and explicit acceptance of action-relative blocking.
- 2026-10-25 — Confirmed by the user: conflict is distinct from a gap and identifies incompatible conditions in the current design. Expose the clash and necessary changes; do not silently choose or relax conditions. Resolution must remain explicit and auditable. Source: the conflict discussion and explicit acceptance.
- 2026-10-25 — Accepted by the user: constraints limit acceptable solutions; satisfying an outcome does not excuse violating a constraint. Boundary resolution must expose conflicts rather than silently relax the boundaries. Formal representation and change procedures remain open. Source: the constraint discussion and the user's acknowledgment.
- 2026-10-25 — Accepted by the user: assumptions can guide explicit hypothetical exploration but cannot justify consequential behavior without sufficient evidence and validation. Track the dependent design and block affected work when material assumptions remain unresolved. Approval to explore is distinct from validation of the claim. Source: the assumption discussion and the user's endorsement.
- 2026-10-25 — Confirmed by the user: decisions form an auditable linked history with motivating sources, affected designs, and revision/replacement relationships. Preserve attribution and distinguish AI proposals from confirmed decisions. Formal records and confirmation mechanics remain open. Source: the decision-history discussion and explicit acceptance.
- 2026-10-25 — Confirmed by the user: lifecycle state must distinguish design readiness, implementation, design validation, behavior validation, and current runtime readiness rather than collapse them into one completion badge. Judgments apply to specific revisions and conditions; exact state names and transitions remain open. Source: the lifecycle-state discussion and explicit acceptance.
- 2026-10-25 — Confirmed by the user: inherit Langflow's existing structural component contracts and extend them with behavioral contracts for assemblies. Type-compatible wiring does not establish semantic correctness or satisfaction of requirements. Detailed contract structure and enforcement remain open. Source: the source-backed Langflow contract discussion and explicit acceptance.
- 2026-10-25 — Accepted by the user: capability describes what an item offers, its required inputs and conditions, results, and limits. These define its offered boundary for comparison with requirements. Capability descriptions are claims; validation and evidence support bounded conclusions about them. Source: the capability discussion and the user's endorsement.
- 2026-10-25 — Confirmed by the user: “boundary resolution” names the key capability that finds the unresolved boundary between requirements above and available realizations below and directs subsequent iteration. Track the affected location, reason, and next action, including multiple simultaneous boundaries. Source: the boundary-resolution discussion and explicit endorsement of the term.
- 2026-10-25 — Confirmed by the user: introduce Configuration below Components as a faithful organizational view of Langflow's existing configuration capabilities. Reuse existing configuration mechanisms rather than reinventing them. Dependencies descend through selected lower-layer items and continue into resource configuration. Source-backed mapping above records the inspected implementation; canvas integration remains pending.
- 2026-10-25 — Confirmed by the user: support independently evolving library items, per-layer assemblies, and instances through dependency-aware revisions. Distinguish elastic working designs from consistent checkpoints; trace changes to determine affected designs and validation. Instances preserve their own configurations and history while referencing shared library items. Source: the versioning discussion and explicit acceptance.
- 2026-10-25 — Confirmed by the user: evidence is the recorded basis for a validation judgment, identifying the subject/version, conditions, and observed result. Evidence supports bounded conclusions and may need renewal after relevant changes. The formal record remains open. Source: the evidence discussion and explicit acceptance.
- 2026-10-25 — Confirmed by the user: distinguish design validation (a coherent blueprint ready to build) from behavior validation (tested behavior after construction). Validation is recursive: constituents, connections/configuration, and each assembly's own requirements must pass applicable checks at every relevant layer. Child successes support but do not establish parent correctness. Failures feed gaps back into refinement. Source: the validation discussion, the user's recursive clarification, and explicit acceptance.
- 2026-10-25 — Confirmed by the user: gaps drive a growing capability library. Resolving missing capabilities should yield reusable building blocks for instances and future requests. As recurring needs become covered, the system should require less invention and more composition; cross-layer assembly remains necessary. Proposed specifications remain distinct from functional, validated items. Source: the gap discussion and the user's repeated explicit acceptance of the growth-and-reuse principle.
- 2026-10-25 — Confirmed by the user: use “connection” for horizontal interaction between items and “composition” for the vertical relationship between a higher-layer item and its realizing assembly. Composition includes mappings between exposed inputs/outputs and internal items; their formal representation remains open. Source: the proposed distinction and the user's explicit acceptance.
- 2026-10-25 — Confirmed by the user: a requirement is something the design must satisfy, even while its implementation remains under exploration. Requirements and further questions emerge through discovery and examination of possible assemblies. Metadata fields remain open. Source: the clarified intent-versus-requirement example and the user's acceptance.
- 2026-10-25 — Confirmed by the user: intent is an incomplete starting expression of the request. Ongoing discovery explores unstated needs and repeatedly clarifies the request through interviewing, assumption challenges, and examination of proposed assemblies. Discovery and assembly evolve together; sufficient clarity for the next decision is required while remaining unknowns stay explicit. Source: the user's clarification and subsequent acceptance.
- 2026-10-25 — Confirmed by the user: assembly has horizontal and vertical directions. Items combine horizontally within a layer; that arrangement bundles vertically into one item at the next layer while retaining its internals. Instance assemblies evolve through iteration, working downward, upward, or between layers, and may remain partially unresolved during design. Source: the user's clarification and explicit acceptance.
- 2026-10-25 — Confirmed by the user: an instance is a purposeful vertical slice of the library stack, rather than merely its persistent workspace. Each instance has the assemblies needed for its intent. Shared library items do not imply shared instance state. The slice need not traverse every layer. Source: the user's definition and subsequent acceptance of the clarified terms above.
- 2026-10-25 — Confirmed by the user: library → layers → items. An item's kind comes from its layer (component, composite component, flow, process, and so on). An instance selects and configures the items it needs across layers. This terminology replaces the earlier “template” wording; no separate template concept is established. Source: the user's correction and explicit acceptance.

## Related records

- [Contracts](contracts.md)
- [Canonical Specification](canonical-specification.md)
- [Knowledge index](README.md)
