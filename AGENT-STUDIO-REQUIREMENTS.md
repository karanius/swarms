# Agent studio — desired capabilities

Started: 2026-10-24
Status: Concept discussion; no implementation authorized by this document.

## Current focus: primitives

Define the fundamental building blocks before designing reusable compositions or the interface around them.

- **Worker:** An individual agent configured to perform work, with a model, instructions, and tools.
- **Tool:** A capability a worker can invoke.
- **Task:** Work to perform, with defined inputs and expected outputs.
- **Coordination pattern:** Rules governing how workers execute and collaborate, including delegation, execution order, parallel work, and completion.
- **Data source:** A resource from which workers obtain information, such as documents, a database, or an API.
- **Memory:** Stored context that workers can retain and retrieve across steps or runs, according to its configured scope.

These are the current proposed primitives. Their exact boundaries and configuration fields remain to be defined together.

Crews, fleets, pipelines, and other saved compositions are not primitives. They are outside the current scope of this list.
