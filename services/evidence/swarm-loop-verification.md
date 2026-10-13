# Real Swarms loop verification

- Backend: services/swarm_loop.py, bound to 127.0.0.1:52417.
- Execution: installed local Swarms 16.0.2 checkout; RoundRobinSwarm with four Agent objects, three rounds.
- Model: EXO Llama-3.2-3B-Instruct-4bit at localhost:52416/v1.
- UI observed 12 completed turns and Three rounds complete.
- Earlier analysis is present in subsequent agent responses and review feedback reaches later rounds.
- Events come from the _execute_agent boundary, not a frontend animation timer.
- Limitation: small model repeated unsupported claims about initialization and bottlenecks; evaluation quality is not established.
- Scope: supplied-facts demonstration; arbitrary canvas graphs and parallel branching are not compiled by this backend.
