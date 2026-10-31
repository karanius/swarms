# Official documentation cross-check for layer contracts

Consulted 2026-10-30. These are upstream documentation facts, not proof of our local executable behavior.

- [Langflow Components overview](https://docs.langflow.org/components/): components expose code-defined inputs/outputs and configuration and pass outputs downstream. Our unchanged native Components plane can ground those identities and fields. This does not define our upper-layer taxonomy.
- [Langflow Run Flow, next documentation](https://docs.langflow.org/next/run-flow): Run Flow invokes another graph and derives dynamic interfaces from it. Nested runs cannot pause for Human Input or agent approval; the documented guidance places approval in the parent. This is a prospective execution constraint, not an integration we ran. A human review policy cannot be called realized merely because two Agent nodes are connected.
- [Versioned Run Flow documentation](https://docs.langflow.org/1.8.0/run-flow): explicit subflow boundaries provide a possible future realization route. Version compatibility must be checked against the pinned local checkout before implementation.

Design inference: containment, data transfer, execution control and human authorization must be different relations with different evidence gates. A Langflow source graph may realize a proposed composite or part of a flow without proving process accountability or task success.
