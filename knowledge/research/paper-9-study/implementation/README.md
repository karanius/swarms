# Market Intelligence reference implementation

This is a local, review-gated implementation of the Paper 9 JSON dataflow. It is not an autonomous profitable-market finder. The canonical JSON controls stage order, typed input bindings, capability identity and output contracts. Pinned native Langflow PythonFunction occurrences invoke trusted, versioned Python resources. They do not execute source text or model-generated code. The resource store and controller have the local user's privileges; this is not an OS sandbox or a remotely authenticated service.

## Supported operation

1. A request contains `brief`, `profile` and `source_catalog`.
2. The controller validates a brief and profile, then creates an isolated run.
3. Discovery screens a supplied source catalog. Optional `web_search_enabled=true` uses bounded public search queries and records failures; only candidate URLs passing the retrieval host policy are fetched.
4. Sources are fetched through existing native SSRF protection with pinned DNS, HTTPS-only exact-host policy, no redirects and bounded bytes/time. Snapshots are hashed and source failures retained.
5. Evidence normalization preserves raw context, exact-hash families and unknown semantic independence/freshness.
6. Existing local model inference proposes source-described alternatives and candidate quotations. Exact quotation matching rejects unsupported invented text. This does not verify the model's interpretation, infer demand or rank profitable opportunities.
7. Assessment records insufficient/pending judgments rather than automatically approving its own claims. The dossier exposes missing evidence, alternatives and cost limits.
8. Independent local review submits a complete rubric for the exact dossier revision. The controller validates and records accept/rework/reject, prevents author self-approval, and only accepted dossiers enter the durable local Content Strategy outbox.
9. A separately acting local consumer can acknowledge the exact outbox record. This is not proof that the future Content Strategy instance is implemented.
10. Refresh conservatively invalidates affected parent claims and produces an approval-gated child-revision request. Automatic new market claims are never generated from a change notice alone.

## Run

Use the existing pinned Langflow environment (no installation is performed):

```
/Users/x/projects/langflow/.venv/bin/python knowledge/research/paper-9-study/implementation/cli.py run --request request.json
```

The request format is supplied as `request.example.json`. It is explicitly an implementation-probe brief, not the user's chosen market or business. Change audience, question, permitted sources and limits before a real investigation. No credentials belong in these files.

Native graph exports have an inert `RUN_ID_REQUIRED` binding. The factory in `ground_native.py` binds a real run identifier to trusted source code; `native_bridge.dispatch` accepts only known stage names and scoped run identifiers. It does not accept arbitrary paths, URLs, source code or model credentials. Raw native definitions are unchanged. No graph is installed into the user's active canvas.

## Persistence and authority

SQLite stores immutable artifact revisions, compare-and-swap run updates, append-only event identities, per-stage leases, exact-revision reviews and idempotent outbox entries. Snapshots remain in the scoped `.runtime` directory. Resume verifies the spec hash, bound input references and stored artifact digests. A new source observation, prompt/model change or input edit requires a new run/revision; it cannot silently rewrite accepted history.

The CLI is a trusted local-user interface, not a security boundary against code running as that user. Reviewer role checks prevent accidental self-approval and wrong-revision delivery; they do not authenticate a remote human. No network listener is created. A future multi-user deployment requires a separately specified authenticated authority adapter before exposure.

Waiting for review pauses the remaining active-execution budget. Review does not replenish consumed compute time. Cancellation prevents subsequent stages; an already blocking retrieval/model call terminates within its configured timeout, rather than being claimed instantaneously killed.

## Cost and evidence boundaries

All stage attempts retain wall time and status, including failures and review gates. Monetary costs, electricity and human review minutes remain unknown unless actually supplied/measured. An unattended stage's zero owner minutes is not a claim of zero total human effort. The assembly ledger is a snapshot; final closure costs include later review/handoff and are separate immutable records.

The source-catalog mode is useful but bounded. Search blocking, incomplete sources, uncertain alternatives or inadequate independent review must produce a qualified/insufficient output. The implementation does not prove factual correctness, completeness of internet search, source independence, market demand or business value.

## Qualification

Run `test_contract.py` for the authored external contract and `implementation/test_*.py` for concrete runtime fixtures. Record actual native component/model/public retrieval probes separately from fixtures. Source policies/weights/commercial rights must be reviewed for the intended business; capturing public documents for this probe is not commercialization clearance. The application does not publish, spend or change accounts.

## Reviewed decisions and child revisions

`cli.py feedback RUN_ID --record feedback.json` accepts a trusted local review bundle containing `assessments`, `recommendation`, and `reason`. Assessment candidate references must match the parent's exact candidate artifact. Every claim is assessed exactly once and all observation references resolve. Supported judgments require an entailment review and the configured reviewer identity. A continue recommendation requires at least one reviewed supported claim. The controller creates a child run, reuses immutable prior evidence checkpoints, and regenerates assessment/dossier/review without overwriting the parent. Continue means continued investigation/Strategy consideration, never profitability proof.

The feedback path has controlled positive and rejection tests. The recorded live document probe remains insufficient; it is not retroactively relabeled a successful market finding. `record-effort` records explicitly owner-reported minutes under a unique event identity; it does not pretend to automatically measure human work.

The public-search option requires both `web_search_enabled=true` and `external_query_authorized=true`. Do not enable it for sensitive text without authority to transmit that query to the search service. Search blocking and result omissions remain visible coverage limits.
