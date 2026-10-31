# Instance Builder Sequence

The intended interaction and construction sequence for the proposed system. This describes the target behavior, not functionality already implemented.

1. **You describe the outcome** naturally.
2. **The system creates an instance**, giving it a name and an initial scope.
3. **Conversation develops a structured specification**, recording requirements, decisions, constraints, and unknowns.
4. **The specification maps onto the instance’s layers**, identifying what each layer must accomplish.
5. **Instructions decompose downward**, defining the smaller capabilities, connections, and acceptance criteria required.
6. **The system checks the library**, reusing existing assemblies and identifying missing pieces.
7. **Assembly proceeds upward:** components → composites → flows → processes → whichever higher layers the instance needs.
8. **Each assembly is tested** against its contract before being treated as working.
9. **Documents and the visual tower update together**, showing what is specified, missing, built, and verified.
10. **Successful assemblies become reusable library entries.**
11. **You refine the outcome through conversation**, and the system updates the affected parts.

Your role is to express intent and resolve meaningful choices. The system handles decomposition, assembly, and verification.

Related: [Instance Compiler Algorithm](INSTANCE-COMPILER-ALGORITHM.md).
