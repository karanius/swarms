# Research: native Jupyter Notebook

The V3 Research tab embeds the upstream Jupyter Notebook 7 application at
`/research-jupyter/tree`. No upstream Jupyter source, CSS, menus or notebook controls are modified.
The same-origin proxy adds a small navigation bootstrap to the HTML response
so local Notebook popups stay in the embedded pane; external links retain
normal browser behavior. It does not style or replace any Jupyter controls.
Native unsaved-change protections remain in effect: save before leaving an
edited notebook.

## Start

From the repository root:

```sh
services/research-notebook/run.sh
cd frontend
npm run dev -- --port 5188
```

The launcher creates a dedicated Python 3.12 environment on first use. It serves
only on `127.0.0.1:5191`, under `/research-jupyter/`. Vite proxies HTTP and kernel
WebSockets on the same origin and adds the local server credential on the server
side. The token remains in `.runtime/token` with mode 0600, never in notebook
content or browser configuration. Authentication and XSRF checks remain enabled.
The kernel is the dedicated environment's Python. Notebook execution has the
local user's permissions; a notebook directory is not an OS sandbox.

## Data

- Active papers: `knowledge/research/notebooks/*.ipynb`.
- Preserved source collection: `knowledge/research/papers.json`.
- Migration backup and mapping: `knowledge/research/notebook-migration/`.
- Paper 2 figures are embedded PNG notebook attachments, without localhost URLs.
  Original SVGs remain in the paper archive. Migration renders SVGs with CairoSVG
  and requires Cairo (already present at `/opt/homebrew/lib` on this Mac).
- The original embedded demonstration notebook is preserved in the migration
  archive. Its code and saved output are copied into Paper 3.

`migrate_papers.py` converts supported BlockNote prose, headings, tables, images
and embedded notebooks, and stops on an unhandled type rather than discarding it.
It never overwrites an existing target notebook. Rerunning is safe for edited
notebooks. It validates notebook file structure; it does not execute cells.

The native Jupyter Save command and autosave write notebook files to disk.
A server-side save hook queues a path-scoped Git commit and push after five
seconds of inactivity, preserving the prior GitHub persistence behavior. Only
saved notebook paths are included; unrelated working or staged files are not
committed. Failures leave the notebook on disk and are recorded in
`.runtime/git-sync.json`; the next save retries. The prior custom browser/disk
sync is not used for notebook editing. Research source JSON is a
migration archive, not a second live representation.

## Functionality checks

Use the native notebook UI to edit, run, interrupt, restart, save and reopen the
Paper 3 demonstration cell. These are integration checks, not research-algorithm
experiments. Do not run every paper or insert study findings during UI checks.

If the service is stopped, run the launcher above and reopen Research. Existing
notebook files and outputs are preserved.
