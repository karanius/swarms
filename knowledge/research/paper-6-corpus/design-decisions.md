# Paper 6 — Research-to-design decisions

Status: proposed design following a targeted primary-source review. No mining or evolutionary experiments performed. This is not an exhaustive or systematic review.

## Shared representation

Proposal: preserve the vendor graph export unchanged, then derive a versioned, typed, attributed, directed multigraph with explicit ports and an open boundary. Keep each source occurrence and source-family membership. A composite candidate references a set of these same occurrences and its exposed boundary; it is not inferred merely from a dense cluster.

[Fong's original thesis](https://arxiv.org/abs/1609.05382) formalizes networks of typed terminals and compositional boundaries. It motivates the interface discipline, but does not establish that Langflow's types instantiate that formalism or that our proposed composites behave correctly. [Speranzon, Spivak and Varadarajan](https://arxiv.org/abs/1802.03080) separately treat abstraction and behavioral contracts; their semantics cannot be inherited just by copying wiring.

| Record | Proposed fields | Purpose |
|---|---|---|
| SourceArtifact | source URL/path, revision, hash, collection time, license, format, fixture flag | Preserve exact evidence and eligibility |
| ComponentOccurrence | source graph, occurrence ID, native type/version, configuration references | Distinguish native definitions from occurrences |
| Port | occurrence, port ID, direction, declared types, required/unknown state | Preserve real interface constraints |
| Edge | source/target occurrences and ports, relation kind, source pointer | Separate data, tool and configuration relations |
| OpenBoundary | membership, incoming/outgoing edges, required unbound inputs | Avoid dropping obligations when proposing packaging |
| CandidateRule | antecedent, consequent, variables, guards, scope, counting semantics, witnesses, counterexamples, unknowns, version | Make implications explicit and auditable |
| EvidenceJudgment | claim, evidence kind, supported/refuted/unknown, provenance | Separate observed structure from inferred purpose and behavior |

## Rule language and evidence

Proposal: start with positive, range-restricted relational rules. Every consequent variable must be bound by the antecedent. Treat absence under incomplete extraction as unknown, not a negative fact. Treat packaging as a separate proposal needing declared criteria. Do not turn a frequent graph motif directly into a semantic implication.

For a fixed rule and declared unit of counting, define antecedent witnesses A and witnesses also satisfying the consequent J. An empirical closed-observation confidence would be |J| / |A| when |A| > 0. It is undefined at zero. This ratio is meaningful only if the consequent is observable for the eligible antecedent cases. Report unknown consequent status separately; do not silently remove unknown cases and present the result as unconditional confidence. AMIE-style PCA confidence, if chosen, must be implemented and named according to its actual definition rather than relabeling this ratio.

Report both artifact-level and source-family-level counts. Exact hashes remove byte-identical copies; they do not remove all tutorial, fork or common-ancestor dependence. Record raw counts, unique hashes and source-family coverage side by side. Thresholds and family definitions remain to be fixed before evaluation.

## Mining and evolution have different jobs

| Approach | Candidate object | Role in the proposed study | Necessary safeguard |
|---|---|---|---|
| Frequent-subgraph discovery | Repeated labeled subgraph | Find reusable structural motifs | No claim of implication or useful boundary from frequency alone |
| Relational rule mining | Conditional relationship | Produce explicit candidate rules with witnesses | Define missingness, denominators, negatives and dependence |
| Typed genetic programming | Typed program/rule expression | Optional search over rule bodies or candidate constructors | Grammar/type constraints plus independent evidence evaluator |
| Graph genetic programming | Indexed graph genotype | Optional search over proposed wiring | Preserve ports, required inputs and acyclicity only where required |
| NEAT | Neural topology and weights | Possible later learned proposal/ranking policy | A separate policy encoding and valid reward; not direct evidence for workflow synthesis |

[DEAP's official GP tutorial](https://deap.readthedocs.io/en/stable/tutorials/advanced/gp.html) documents typed primitives and warns that generation can fail when suitable terminals are unavailable. Typed generation is therefore a constraint mechanism, not a completion guarantee. [The original NEAT paper](https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf) concerns neural topology and weight evolution. Applying it to this corpus would require a new mapping and evaluation problem; rapid discovery of layer rules is unproven.

Recommendation: use one relationship representation for mining, deterministic checks and optional evolutionary proposals. Keep the checker outside the proposal process. Begin with relational mining and transparent baselines; add evolutionary search only as an explicitly measured comparison, not a presumed improvement.

## Evaluation and claim boundaries

[Process discovery](https://processmining.org/process-discovery.html) uses event logs; static workflow exports are not those logs. We can investigate design regularities now, not observed runtime conformance or performance. [Dwork et al.](https://papers.neurips.cc/paper_files/paper/2015/hash/bad5f33780c42f2588878a9d07405083-Abstract.html) show why adaptively reused evaluation data can overfit. Our practical proposal is a versioned exposure ledger and source-family-disjoint evaluation. We do not claim their formal guarantees without implementing their mechanisms and meeting their assumptions.

| Gate | Required evidence | What it does not establish |
|---|---|---|
| Corpus gate | All origins recorded; incompatible formats separated; snapshot frozen | Production quality |
| Extraction gate | Auditable examples and reference facts, including unknowns and boundaries | Runtime behavior |
| Rule gate | Explicit conditions, denominators, witnesses and exceptions | Causality or semantic necessity |
| Generalization gate | Predeclared evaluation on separate source families; revisions logged | All future libraries |
| Composite gate | Typed boundary and obligation preservation with justified formation criteria | Task success without behavioral tests |

## First bounded implementation, following the recorded protocol

1. Freeze eligible sources and assign source-family groups.
2. Extract occurrences, typed ports and actual edge relations with source pointers.
3. Hand-check representative exports and difficult cases before bulk mining.
4. Compare frequency-only motifs with bounded relational rules.
5. Produce one auditable rule card: meaning, variables, scope, counts, missingness, sources, exceptions and limitations.
6. Evaluate frozen rules on separate families. A failure revises the versioned design rather than rewriting the original hypothesis.

No experiment results are asserted here. The immediate deliverable is a literature-grounded representation and protocol; composite generation remains a later inference and validation problem.

## Method-specific cautions from the collected primary papers

| Source | What was inspected | Supported distinction | Consequence for our design |
|---|---|---|---|
| [gSpan original](https://sites.cs.ucsb.edu/~xyan/papers/gSpan.pdf) | Preserved reading notes: visually inspected title page and abstract; historical PDF text encoding was defective | Frequent structural patterns and canonical DFS representations | Motif baseline only; directed ports need an explicit encoding and implementation checks. Do not claim full-paper reproduction. |
| [AMIE 3 author manuscript](https://www.luisgalarraga.de/docs/amie3.pdf) | Preserved reading notes: definitions and algorithm discussion in Sections 3–4, plus opening material | Relational Horn rules; support, head coverage and confidence have different meanings | Fix the fact encoding and counting policy before using library scores; PCA confidence requires a justified missingness assumption. |

For AMIE-style measures, a support count and head coverage are not interchangeable with the fraction of graph transactions containing a motif. Keep engine-native scores and our graph/family-level reports separately named, with their denominators. Exactness refers to the selected engine mode within its specified search space and assumptions, not to semantic truth of workflow rules.
