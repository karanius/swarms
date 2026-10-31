# Metadata-driven composition workbook

A working template for describing available capabilities, expressing a desired outcome, and deriving reusable compositions. This is a custom workbook for our discussion, not a formal industry standard.

Work in metadata first. Keep the description of a capability separate from the executable component that implements it. Mark statements as desired, documented, or tested.

## 1. Intent

I want to work with a symbolic metadata representation of Langflow's existing components—their capabilities, inputs, outputs, dependencies, and constraints—to discover and design useful combinations without repeatedly starting from scratch.

I want to express a desired capability, use explicit composition rules and model-assisted guidance to derive candidate composite components, and validate those candidates against the intended outcome. Validated composites should become reusable building blocks that can themselves be combined into higher-level flows and larger compositions.

The purpose is to build, experiment with, and refine agent workflows faster while keeping the relationship between metadata, actual executable capabilities, and observed results clear.

### Scope

- Use Langflow's existing components and execution capabilities as the starting inventory.
- Define metadata, relationships, and composition rules that support finding and evaluating combinations.
- Grow a library of reusable composites, including agent workers, crews, and coordination patterns as appropriate.
- Identify missing capabilities explicitly rather than assume metadata alone supplies them.

### Success criteria

- A desired capability can be described using the same vocabulary as the component catalog.
- Each candidate composition identifies its constituent components, connections, requirements, and constraints.
- Candidates can be checked against explicit acceptance criteria, with runtime evidence for claims that require execution.
- A validated composite can be saved, reused, and combined with other building blocks without rebuilding its internals.
- Reusing a validated composite takes fewer manual assembly steps than reconstructing the equivalent flow from primitives; compare both on the same example task.

## 2. Vocabulary and schema

### Metadata record types

| Record | Definition |
|---|---|
| Component | A reusable building block, classified as primitive or composite. |
| Capability | What a component can accomplish, including the conditions and limits of that claim. |
| Connection | How component instances exchange information or control execution. |
| Rule | A condition that determines whether a proposed composition is valid or invalid. |

These are metadata record types, not four executable primitives. A record describes something; the referenced implementation performs the work.

### Primitive and composite

- **Primitive:** Reusable and indivisible at the chosen level of composition. Its implementation may have internal parts, but those are not separate building blocks at this level.
- **Composite:** A reusable assembly of component instances and their connections. Its members may be primitives or other composites.
- **Component definition:** The reusable description of a building block.
- **Component instance:** One use of a particular component definition and version within a composition. Multiple instances may use the same definition with different configurations.

Workers, tools, tasks, coordination patterns, data sources, and memory remain the agreed candidate building-block categories. Their precise representation will be mapped against Langflow's available components; a category name alone does not establish an executable implementation.

### Component schema

Primitive and composite components share these fields:

| Field | Value | Required |
|---|---|---|
| Identity | Stable component ID | Yes |
| Version | Version identifier for the definition | Yes |
| Name | Human-readable name | Yes |
| Description | Purpose and intended use | Yes |
| Kind | Primitive or composite | Yes |
| Category | Classification term | Yes |
| Capabilities | References to capability records | Yes; may be empty while unknown |
| Inputs | Named ports with data types, meanings, and whether each is required | Yes; may be empty |
| Outputs | Named ports with data types and meanings | Yes; may be empty |
| Requirements | Dependencies, configuration needs, and credential references; never credential values | Yes; may be empty |
| Constraints | References to applicable rules and declared limits | Yes; may be empty |
| Implementation | Reference to executable code or a flow, or explicitly not implemented | Yes |
| Evidence | Sources or test results supporting the description, with claim status | Yes; may be empty while unknown |
| Composition | Member instances, their definition/version references and configurations, internal connections, and external-to-internal port mappings | Required for composites |

An empty list means none recorded; it must not silently imply that the component has no requirements or limitations. Evidence distinguishes unknown, desired, documented, and tested claims.

### Capability schema

- **Identity and name:** Stable ID and human-readable label.
- **Description:** The outcome the capability supports.
- **Conditions and limits:** Preconditions, applicable scope, and known limitations.
- **Evidence:** Supporting documentation or execution tests, with claim status.

Component records reference capability records so the same capability can be associated with multiple implementations.

### Connection schema

- **Identity:** Stable ID within the composition.
- **Source and target:** Component-instance references and the relevant ports or control endpoints.
- **Relationship type:** Data exchange or execution control, with its precise meaning defined in section 4.
- **Mapping:** Any explicit data transformation or routing configuration.
- **Applicable rules:** References to compatibility and execution rules.

### Rule schema

- **Identity and description:** Stable ID and the condition being expressed.
- **Scope:** The components, connections, or compositions to which it applies.
- **Condition:** The predicate or constraint to evaluate.
- **Verification method:** Metadata validation, execution test, or explicitly unresolved.
- **Evidence:** The basis for the rule and results of any checks performed.

Mandatory rules determine validity. Preferences rank otherwise valid candidates; they must be labeled separately from mandatory rules.

## 3. Available components

Inventory from the running Langflow component catalog: **208 component definitions across 32 categories** (130 current, 78 legacy). Names only for this first pass; full metadata can follow.

Availability here means registered in this installation. Some components require credentials, models, external services, or additional configuration; their execution has not been validated by this inventory.

### Current components

- **Custom Components:** Custom Component.
- **Data Sources:** API Request; Mock Data; SQL Database; URL; Web Search.
- **Files & Knowledge:** File System; Knowledge; Memory Base; Read File; Write File.
- **File Ingestion:** File Content Retriever; File Description Generator; Merge Flows.
- **Flow Control:** Human Input; If-Else; Listen; Loop; Notify; Run Flow.
- **Input & Output:** Chat Input; Chat Output; Webhook.
- **LangChain Utilities:** Character Text Splitter; CSV Agent; Fake Embeddings; HTML Link Extractor; Language Recursive Text Splitter; Natural Language Text Splitter; OpenAI Tools Agent; OpenAPI Agent; Prompt Hub; Recursive Character Text Splitter; Runnable Executor; Semantic Text Splitter; SQLAgent; SQLDatabase; Tool Calling Agent; XML Agent.
- **LLM Operations:** Batch Run; Guardrails; LLM Selector; Smart Router; Smart Transform; Structured Output.
- **Models & Agents:** A2A Agent; Agent; Embedding Model; Language Model; MCP Tools; Message History; Prompt Template.
- **Processing:** Data Operations; Dynamic Create Data; Parser; Split Text; Type Convert.
- **Triggers:** Inbound Webhook; Schedule.
- **Utilities:** Calculator; Current Date; Python Interpreter.
- **Amazon:** Amazon Bedrock Converse; Amazon Bedrock Embeddings; S3 Bucket Uploader.
- **Anthropic:** Anthropic.
- **Azure:** Azure OpenAI; Azure OpenAI Embeddings.
- **Cohere:** Cohere Embeddings; Cohere Language Models; Cohere Rerank.
- **DataStax:** Astra DB; Astra DB Chat Memory; Astra DB CQL; Astra DB Data API; Graph RAG; Hyper-Converged Database.
- **Cassandra:** Cassandra; Cassandra Chat Memory; Cassandra Graph.
- **Docling:** Chunk DoclingDocument; Docling; Docling Serve; Export DoclingDocument.
- **Google:** BigQuery; Calendar: Create Event; Calendar: List Events; Drive: Fetch File (app files); Drive: List Files (app files); Gmail: On Message; Gmail: Send Email; Google Calendar: On Event; Google Drive: On File; Google Generative AI; Google Generative AI Embeddings; Google Serper API.
- **IBM:** IBM Db2 Vector Store; IBM watsonx.ai; IBM watsonx.ai Embeddings; IBM watsonx.data MCP; IBM watsonx.data Presto.
- **Microsoft:** OneDrive or SharePoint: On File; Outlook Calendar: Create Event; Outlook Calendar: List Events; Outlook: On Calendar Event; Outlook: On Message; Outlook: Search Mail; Outlook: Send Mail; SharePoint/OneDrive: Fetch Item; SharePoint/OneDrive: List Items; Teams: Post Channel Message; Teams: Post Chat Message.
- **Ollama:** Ollama; Ollama Embeddings.
- **OpenAI:** OpenAI; OpenAI Embeddings.
- **Oracle:** Oracle Autonomous Database Loader; Oracle Doc Loader; Oracle Embeddings; Oracle Vector Store.
- **Slack:** Slack: Add Reaction (as app); Slack: Create Canvas (as user); Slack: List Channel Members (as app); Slack: On Message; Slack: On Reaction; Slack: Post Message (as app); Slack: Read Thread (as user); Slack: Search (as user); Slack: Send Message (as user).
- **ToolGuard:** Policies.

### Legacy components

Loaded in the catalog but marked legacy; they may be hidden by default in the interface.

- **Agentics:** aGenerate; aMap; aReduce.
- **CrewAI:** CrewAI Agent; Hierarchical Crew; Hierarchical Task; Sequential Crew; Sequential Task; Sequential Task Agent.
- **Data Sources:** Load CSV; Load JSON; News Search; RSS Reader.
- **Embeddings:** Embedding Similarity; Text Embedder.
- **Files & Knowledge:** Directory; Knowledge Base; Knowledge Ingestion.
- **Flow Control:** Condition; Flow as Tool; Pass; Sub Flow.
- **Input & Output:** Text Input; Text Output.
- **LangChain Utilities:** ConversationChain; JsonAgent; LLMCheckerChain; LLMMathChain; Natural Language to SQL; Retrieval QA; Self Query Retriever; VectorStoreInfo; VectorStoreRouterAgent.
- **LLM Operations:** Guardrails (Legacy).
- **Processing:** Alter Metadata; Combine Data; Combine Text; Create Data; Create List; Data to Message; Data → DataFrame; Extract Key; Filter Data; Filter Values; JSON Cleaner; JSON Operations; Message Store; Message to Data; Output Parser; Parse DataFrame; Parse JSON; Regex Extractor; Select Data; Table Operations; Text Operations; Update Data.
- **Prototypes:** Python Function.
- **Tools:** Calculator; Google Search API [DEPRECATED]; Google Serper API [DEPRECATED]; Python REPL; Search API; SearXNG Search; Serp Search API; Wikidata API; Wikipedia API; Yahoo! Finance.
- **Utilities:** ID Generator.
- **Amazon:** Amazon Bedrock.
- **DataStax:** Astra DB Graph; Astra DB Tool; Astra Vectorize; Dotenv.
- **Google:** Gmail Loader; Google Drive Loader; Google Drive Search; Google OAuth Token; Google Search API.

**Source:** Authenticated catalog returned by the local Langflow service (`/api/v1/all`), captured for this inventory. Categories follow the service catalog, including provider bundles and entries outside the default sidebar groups.

## 4. Relationships and composition semantics

- What relationships can exist between components?
- What does each relationship mean when executed?
- How does information move between them?
- How are state and memory shared or isolated?
- How does a composition expose its external inputs and outputs?

**Record:** relationship types, permitted endpoints, and execution meanings.

## 5. Rules and constraints

- Which connections are compatible?
- What must exist before an operation can run?
- What combinations are forbidden?
- What ordering, concurrency, resource, permission, and stopping constraints apply?
- Which requirements are mandatory, and which are preferences?

**Record:** explicit rules with a pass/fail check or a stated verification method.

## 6. Desired capability

Describe what a candidate reusable must do before deciding its internal composition:

- Capability requested.
- Required inputs and outputs.
- Acceptance criteria.
- Mandatory constraints.
- Preferred qualities and tradeoffs.
- Concrete examples and counterexamples.

**Record:** a target capability specification using the same vocabulary as the catalog.

## 7. Derivation and evaluation

- Which existing capabilities could satisfy the target?
- What candidate compositions follow from the relationships and rules?
- Which conditions can metadata establish, and which require execution?
- How will candidates be ranked?
- What tests would confirm or reject each candidate?

**Record:** candidate composition graphs, their rationale, rule-check results, and execution evidence when available.

A model may propose candidates. Metadata checks and runtime tests provide different kinds of evidence; neither should be reported as the other.

## 8. Gaps and next steps

- Which requirements are already satisfied?
- Which need configuration or a composition of existing components?
- Which require a new implementation?
- Which remain unknown because evidence is missing?
- What depends on what, and what is the smallest useful next step?

**Record:** a gap ledger and a dependency-ordered roadmap, with an acceptance check for each item.

Once a composition passes its acceptance checks, describe it with the same catalog schema so it can be reused in later compositions. Preserve its internal graph and evidence.

## Working discipline

- Give entities stable identities; names can change.
- Version definitions and record which versions a composition uses.
- Trace each claim to its source or test.
- Keep desired capabilities separate from available capabilities.
- Record unknowns explicitly.
- Change the model deliberately when evidence contradicts it.
