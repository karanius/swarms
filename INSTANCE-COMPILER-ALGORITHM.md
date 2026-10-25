# Instance compiler algorithm

Status: proposed architecture, not yet implemented. Agreed direction from the instance-builder discussion.

## Purpose

Translate conversational intent into instructions that decompose requirements downward, then assemble executable components upward into reusable compositions. Apply the same mechanism at any useful composition level; the library's layer names are classifications rather than mandatory stages.

## Foundations

This is a proposed combination of established methods, not an algorithm supplied by Matt Pocock's skills.

- Matt-inspired discovery, domain modeling, and Wayfinder skills provide the conversation-to-specification front end: https://github.com/mattpocock/skills
- Hierarchical Task Network planning provides recursive decomposition: https://www.cs.umd.edu/~nau/papers/nau2003shop2.pdf
- Syntax-guided synthesis provides constrained candidate assembly: https://arxiv.org/abs/2312.06001
- Counterexample-guided synthesis provides a generate-check-repair loop: https://people.csail.mit.edu/asolar/SynthesisCourse2020/Lecture10.htm

## Algorithm

1. **Compile the conversation into a contract.** Extract desired behavior, inputs, outputs, constraints, examples, and acceptance criteria. Keep assumptions explicit. Maintain the specification as the conversation evolves.
2. **Look for an existing implementation.** Search the library for a component or saved composition satisfying that contract. Reuse it if its configuration and evidence fit.
3. **Otherwise, decompose the contract.** Produce child contracts, connections, and coordination instructions. Each child has a concrete responsibility. Check that the children collectively address the parent's requirements.
4. **Repeat downward.** Continue until every leaf maps to an executable component. For an absent capability, generate a bounded implementation task; build and test it, or report the gap.
5. **Assemble upward.** Configure leaves, connect them according to the generated instructions, and package the assembly behind the parent's input/output interface.
6. **Check the parent contract.** Validate connections and run acceptance checks. Feed failures back into configuration, wiring, or decomposition; retry within a budget.
7. **Register and repeat.** Save successful assemblies as versioned reusable components, preserving contracts, internals, dependencies, and evidence. They become available building blocks for their parents.

## Pseudocode

```text
BUILD(contract, library, budget):
    if budget exhausted:
        return UNRESOLVED(contract)

    candidate = find_reusable(contract, library)
    if candidate exists and CHECK(candidate, contract) passes:
        return candidate

    if contract is directly implementable:
        candidate = configure_or_implement(contract)
    else:
        children, wiring, coordination = DECOMPOSE(contract)

        CHECK_REQUIREMENT_COVERAGE(contract, children, wiring)

        implementations = []
        for child in dependency_order(children):
            implementation = BUILD(child, library, remaining_budget)
            if implementation is UNRESOLVED:
                return GAP(contract, child)
            implementations.append(implementation)

        candidate = PACKAGE(implementations, wiring, coordination,
                            interface=contract.inputs_and_outputs)

    result = CHECK(candidate, contract)

    if result fails:
        return REPAIR_AND_RETRY(contract, candidate, result, remaining_budget)

    library.register(candidate, contract, result.evidence)
    return candidate
```

The pseudocode is conceptual: its uppercase operations require implementations. A production controller must propagate both unresolved results and gaps, charge all recursive work and retries to a shared budget, detect dependency cycles, and check requirement coverage before assembly proceeds. Static coverage does not establish behavioral correctness.

## Instructions generated at every composition boundary

- Child component references and versions.
- Configuration for each child.
- Input/output mappings.
- Execution order, parallelism, routing, or loops.
- Shared state, failure handling, and stopping conditions.
- Acceptance checks for the assembled parent.

These are the assembly recipe for the parent. Requirements travel downward as contracts and recipes. Implementations return upward as packaged, checked components.

A component does not rewrite itself into a higher layer. The compiler assembles components into a new reusable component. The same recursive operation serves composites, full flows, and higher-level compositions.

## Evidence and boundaries

- Missing implementations remain explicit gaps or bounded build tasks, not functional-looking catalog labels.
- Confirmed user decisions, assistant assumptions, design proposals, assembled implementations, and runtime evidence remain distinct.
- For open-ended agent behavior, passing tests establishes evidence within the tested scope, not universal correctness.
- The current Pi instance builder produces design records and proposed tower manifests. It does not yet implement this compiler.
