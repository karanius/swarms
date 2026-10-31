# Guided Instance Builder with Pi

A Rich terminal interface that captures an outcome, resumes an instance, and runs conversational discovery through Pi. Pi is pinned locally in `package-lock.json`; no global installation is required.

## Start

```sh
python3 /Users/x/projects/swarms/services/instance-builder/instance_builder.py
```

For another checkout: create `.venv` in this directory, install `requirements.txt` into it, and run `npm ci` here. Requires Python 3.10+ and Node.js 22+.

Create or resume an instance, then choose **C — Continue discovery**. Pi uses the standalone API Proxy copied from `karanius/template/services/api-proxy` at repository revision `87f5744`. The proxy defaults to `http://127.0.0.1:8787/v1` and owns sign-in and model selection.

**M — Model setup** checks the local API, signs in through API Proxy if needed, and starts its API in the background. It remains running when you return to the builder. Configure model choices using `../api-proxy/run.sh config set`; Pi discovers the selected model through `/v1/models`. No separate Pi provider key is required. Use `INSTANCE_BUILDER_PROXY_URL` to select another compatible proxy base URL. Pi's generated local provider configuration and proxy log are ignored under `.pi-runtime/`.

## Conversation loop

1. Orient from the saved instance, without needing this chat or a previous Pi session.
2. Propose a name, summary, relevant tower blocks, and next discovery question.
3. Review the proposed update: accept or discard.
4. Reply naturally; Pi proposes corresponding decision, vocabulary, map, and tower changes.
5. Accept to persist; leave or resume at any point.

Use **B** at menus or **/back** at text prompts to return. **Q** or **/quit** exits. **E** edits the outcome before discovery. Changing an outcome after discovery requires restoring its wording or creating a new instance; existing decisions are preserved rather than silently reinterpreted. In discovery, **T** shows the proposed tower and **D** shows document locations. Single-letter T/D/M replies are reserved for navigation.

## Persistent instance workspace

Default private storage: `.instances/`. Existing outcome JSON files remain compatible. Each discovery instance gains a `workspaces/<instance-id>/` directory:

- `state.json`: authoritative model, accepted conversation, decisions, and tower.
- `INTENT.md`, `MAP.md`, `DECISIONS.md`, `GLOSSARY.md`, `SPEC.md`: generated document views.
- `tower.json`: proposed tower manifest, ready for a future canvas adapter.

The controller atomically commits accepted state and regenerates document views. Edit through discovery; direct edits to generated Markdown are overwritten on projection. Every Pi request reconstructs its context from accepted state. Pi sessions are ephemeral and tools/extensions are disabled for this discovery stage. The controller owns all writes.

## Skills

`skills/` contains Orient, Chart, Explore, Define, Reconcile, and Specify. These are original, instance-oriented instructions inspired by Matt Pocock's decision-tree exploration, domain modeling, and Wayfinder approach. They are loaded into each discovery request. No external issue tracker is contacted.

## Validation and limits

```sh
.venv/bin/python -m unittest discover -v
```

Checks cover navigation, persistence, fresh context construction, decision preservation, dependency cycles, invalid output, and provider failures. Model proposals require review; quoted evidence alone is not proof that the interpretation is correct. This implementation produces a tower manifest; the existing canvas is not yet synchronized. Research tools and implementation execution are not enabled. Live verification through API Proxy succeeded: a fresh Pi process received the Da Nang housing intent, returned a proposed name and three tower blocks, and asked for the monthly housing budget. This was an isolated verification call; the user’s saved instance was not modified. Pi uses the proxy’s native Responses route because its Chat Completions route rejects Pi’s array-form text content.

## Delegated walkthrough and completion

In discovery, `/assume TEXT` supplies assistant-authored defaults. These can update assumptions but cannot create confirmed user decisions. `/finish` saves `HANDOFF.md`, marks the design handoff ready, preserves open research questions, and returns to the instance review screen. This finishes design, not research or implementation.
