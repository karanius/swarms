# Bounded rule-learning protocol, frozen before outcome inspection

## Question and scope
Can AnyBURL, called through PyClause, learn explicit local feature implications and recover one masked saved connection feature on source-separated examples? Can the resulting head be written as a component-group proposal with declared ports and unresolved configuration?

This is an exploratory, retrospective study. The corpus has already been exposed by previous analyses; the new source-group split is not pristine held out. It is not behavioral validation, autonomous composite-boundary discovery, or higher-layer generation. No additional graph UI is planned.

## Input and isolation
Use frozen `patterns/transactions.json` and the source-preserving topology extraction. One subject is a graph-scoped center occurrence, never a component type. Triple `(center,has_feature,f)` encodes one observed incident feature `(centerType,direction,neighborType,sourcePort,targetPort)`. The feature is a vocabulary constant; its exact source edge witnesses remain separately retained.

Split whole recorded provenance groups using SHA256 of `paper6-relational-v1:` plus family ID: integer first8hex modulo5==0 is evaluation; all others training. Do not rebalance based on outcomes. Known copied origins were unioned in the earlier extraction; modified copies can remain undetected. Recompute the association guidance from training transactions only; do not reuse the all-corpus association catalog for selection.

## Engines and accepted language
Pin PyClause source and its shipped AnyBURL JAR by hash. Run three serial AnyBURL feature-learning attempts, 20 seconds each, one worker, max cyclic body2 / acyclic body1, support threshold2 / confidence.0001, Java heap512MB; process timeout75 seconds and required output checks. Random seed is not controlled, so repeated runs are stochastic stability observations, not deterministic reproducibility guarantees.

Only accept `has_feature(X,fB) <= has_feature(X,fA)` with the identical subject variable and known feature constants, distinct features and the same center type. Reject all other shapes, center-specific constants, multi-subject bridges and tautologies. This is a relational serialization of local association, not discovery of arbitrary graph topology. Independently recount exact training body and joint counts; require joint>=5, >=2 recorded source groups, confidence>=.5 and lift within center type>=1.05. Keep native learner counts separately.

## Comparisons
1. Accepted AnyBURL rules with max-confidence ranking.
2. Same rules shortlisted to the top100 unordered training-only FP-Growth pairs, ranked by joint source-group breadth, graph count, count and canonical key. This tests post-learning guidance, not faster learning or a different input dataset.
3. Exhaustive same-language counting baseline with identical thresholds.
4. Center-type frequency baseline: predict an unobserved feature common around that center type, without using another feature.

Retain all training facts for the learner. Do not feed only the shortlisted features. A separate 20-second typed-port occurrence-edge learning probe may record how many transferable binary rules appear; this uses a different representation and is not scored as equivalent to the feature recovery task.

## Masking and measures
For each evaluation neighborhood with >=2 features, choose exactly one masked feature by deterministic SHA256 of subject and feature. Retain up to1000 cases by deterministic case-ID hash, fixed before observing results. Remove the target feature triple completely; only visible features enter native query answering. Do not remove merely one duplicate source edge while leaving the same feature. Queries are fixed subjects with relation `has_feature`, known answers filtered. Load training facts plus partial evaluation facts to supply the known vocabulary; the strictly one-subject one-body rule language cannot traverse training/evaluation centers.

Report cases, train/evaluation graphs and families, vocabulary coverage, answered cases, top1 exact masked-feature recovery, recovery/case, recovery/answer, and macro family recovery. Not matching the one recorded target does not establish an invalid alternative. Do not call unobserved saved edges false behavioral outcomes. Native scores use zero unseen smoothing and max aggregation; ties are ranked canonically in the separate audit.

## Proposal contract
For recoverable or incorrect predicted heads, build a synthetic design proposal from the visible body edge and a predicted incident-edge feature. Resolve node/port declarations from training examples only, preserving references, types and versions. The added neighbor is explicitly a fresh symbolic occurrence; aliasing to an existing neighbor is unresolved. Expose all declared required input fields not supplied by the two planned edges, and keep credential field names/binding unknowns. Check connectedness, acyclicity, port declaration presence and declared type-label overlap. These are necessary saved-schema checks, not runtime activation or usefulness. Required configuration fields with no wire are unresolved, not proven absent. Reject self-loop synthesis and unknown catalog descriptors.

## Verification and reporting
Controlled fixtures must challenge graph/center isolation, duplicate masking, unsupported rule syntax, denominator counting, training-only guidance, unknown vocabulary, contradictions/required-input exposure and proposal source references. A separate verifier must reconstruct counts and masked targets from frozen source records, confirm no family overlap, compare native rule predictions with direct one-body application, inspect every saved proposal and preserve all failure cases. Notebook cells must actually run; their outputs, tables and charts must match the saved evidence. Update Sections6–9 and the discussion/conclusion without changing the original abstract or existing explorers. Report limitations and negative results without tuning thresholds after inspection.

## Engineering corrections before the final run

Static review prompted explicit disabling of all QA early stopping (the16-answer regression passes), fresh per-invocation engine directories, rejection of preexisting output artifacts, and full independent baseline/proposal recounts. The initial typed-wire probe exhausted the fixed512MB Java heap during relation-index preparation. The final pipeline preserves that as an infrastructure failure rather than treating it as zero learned rules or discarding the successful feature task. Budgets, split, thresholds, accepted language and primary measures remain unchanged. Earlier raw engine files/logs are retained; final results use a fresh batch.
