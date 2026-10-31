# Programmable workflow repositories

Saved: 2026-10-24

Goal: quickly design programmable workflows with explicit inputs, reusable steps, and declared outputs.

Declaring workflow inputs and outputs is widely supported. Declaring only the desired result and having an engine infer the steps is less common: these tools generally require you to define the transformations. These repositories focus on workflow creation and execution, though some also include adjacent features.

| # | GitHub repository | How you design workflows | Input → output model | Best fit / tradeoff |
|---|---|---|---|---|
| 1 | **[Kestra](https://github.com/kestra-io/kestra)** | Declarative YAML, visual editor, or AI-assisted authoring | Workflow inputs, task outputs, expressions, and final outputs | Strongest overall match: fast authoring with branching, parallelism, subflows, and execution visibility. |
| 2 | **[Windmill](https://github.com/windmill-labs/windmill)** | Write scripts and compose them in a flow editor | Script arguments become inputs; returned results feed downstream steps | Best for programmable workflows: reusable Python/TypeScript scripts with visual composition. Also includes app-building features. |
| 3 | **[Dagu](https://github.com/dagucloud/dagu)** | Compact YAML around existing scripts and commands | Parameters, step outputs, artifacts, and file inputs/outputs | Best lightweight local option: one binary with a web UI; easy to wrap tools you already use. |
| 4 | **[n8n](https://github.com/n8n-io/n8n)** | Visual node canvas with custom code | Map incoming data through nodes into downstream results | Best for fast integration workflows: APIs, services, and AI calls. Uses fair-code licensing. |
| 5 | **[Activepieces](https://github.com/activepieces/activepieces)** | Visual builder with reusable TypeScript “pieces” | Trigger inputs and step results mapped into subsequent actions | Best for reusable automation blocks: supports branches, loops, code, and human input. |
| 6 | **[Conductor](https://github.com/conductor-oss/conductor)** | Declarative workflow definitions and SDKs | Workflow/task inputs and outputs with explicit data mappings | Best for distributed service workflows: durable execution across workers; more infrastructure to operate. |
| 7 | **[Prefect](https://github.com/PrefectHQ/prefect)** | Python functions decorated as flows and tasks | Function parameters → returned values | Best if you want to program directly in Python: flexible control flow; authoring primarily happens in code. |
| 8 | **[Snakemake](https://github.com/snakemake/snakemake)** | Rules declaring inputs, outputs, and execution commands | Request a target file; the engine resolves the necessary dependency chain | Closest to “declare the output I want”: particularly strong for file-based processing pipelines. |
| 9 | **[Nextflow](https://github.com/nextflow-io/nextflow)** | A dedicated workflow language connecting processes | Explicit process inputs/outputs connected through data channels | Best for parallel computational pipelines: portable across local, cluster, and cloud execution. |
| 10 | **[Argo Workflows](https://github.com/argoproj/argo-workflows)** | YAML templates arranged as steps or dependency graphs | Explicit input/output parameters and artifacts | Best for container workflows on Kubernetes: powerful execution model, with Kubernetes as a prerequisite. |

## Recommended shortlist

- **Kestra:** declarative workflow design.
- **Windmill:** code plus visual composition.
- **Snakemake:** specify the output and let the engine determine which supplied rules must run. It does not invent the implementation. See the [official tutorial](https://snakemake.readthedocs.io/en/stable/tutorial/basics.html).

The repository links above are the primary sources used for this comparison. This is a research shortlist, not a hands-on benchmark.
