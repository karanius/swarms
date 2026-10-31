# Community GitHub Langflow graph corpus

Collected at 2026-10-29T17:44:40.731947+00:00.

- Repositories inventoried: 376
- Repositories with graph JSON: 218
- Raw graph-bearing JSON artifacts: 2767
- Distinct SHA256 byte contents: 1296
- Exact duplicate artifact instances: 1471
- Downloaded artifact bytes: 350644939
- Failures recorded: 7

## Discovery

Primary GitHub repository search API queries, sorted by stars, first 100 results per query (search response snapshots retained):

- `langflow templates`
- `langflow workflows`
- `langflow flows`
- `langflow json`
- `langflow tutorial`
- `langflow rag`
- `langflow agents`
- `langflow examples`

The search-result ceiling is a discovery limit, not exhaustive coverage of all public GitHub repositories. GitHub default repository search excludes forks unless explicitly requested. Sources outside langflow-ai were selected from these results; mirrored/copied source families can still exist and are not presumed independent.

## Collection and exclusions

Each repository is pinned to its default-branch commit at collection. Recursive Git trees inventory JSON paths. All JSON candidates between 21 bytes and 8 MB are inspected, excluding node_modules and Python environment paths and package lockfiles. A graph-bearing JSON requires a nodes array, edges array, and at least one node with data or type; nested graph objects and arrays are inspected. Raw bytes are saved without normalization. This broad structural gate still requires Langflow-specific downstream validation.

License text is collected from LICENSE, COPYING and NOTICE basenames (up to 200 KB each; up to ten files per repository). Reported SPDX values originate from GitHub metadata. Presence of license text does not establish its scope over every flow. Missing licenses remain unknown. No downloaded code was executed and no repository dependencies were installed.

Initial JSON scanning guard: first 500 eligible paths per repository. Remaining limits are listed below; successful source counts do not prove independence or permission. Non-JSON embedded examples, archives, branches other than default, Git LFS payloads, and inaccessible submodules are not collected.

## Coverage limits

No collected repository hit the recursive-tree truncation or 500 eligible JSON guard.

## Sources with graph artifacts

| Repository | Pinned commit | Artifacts | License metadata |
|---|---|---:|---|
| [Empreiteiro/langflow-templates](https://github.com/Empreiteiro/langflow-templates/tree/6135b48e3700d5db93e2352bd0a8345cb144937e) | `6135b48e3700d5db93e2352bd0a8345cb144937e` | 155 | unknown; unknown |
| [lien0219/openxflow](https://github.com/lien0219/openxflow/tree/40e135d45307424f0589108d43d7d915246dccda) | `40e135d45307424f0589108d43d7d915246dccda` | 123 | MIT; license-text-collected; review-required |
| [aliyuzerler/langflow_ai](https://github.com/aliyuzerler/langflow_ai/tree/93e364fa6bc2029d175c92477748d71f7bb86172) | `93e364fa6bc2029d175c92477748d71f7bb86172` | 121 | MIT; license-text-collected; review-required |
| [malepti/workflowsAURA-LangFlow](https://github.com/malepti/workflowsAURA-LangFlow/tree/dbca774cbf5fd53e0f2752ce24ddb6cc4b11fe43) | `dbca774cbf5fd53e0f2752ce24ddb6cc4b11fe43` | 121 | MIT; license-text-collected; review-required |
| [MarcusService/dsh-limited-langflow-ai__langflow-20261029](https://github.com/MarcusService/dsh-limited-langflow-ai__langflow-20261029/tree/88ff77e5b1bf1f50beede25cd01f068934e11795) | `88ff77e5b1bf1f50beede25cd01f068934e11795` | 117 | MIT; license-text-collected; review-required |
| [zhysga/multi_agent_coope_with_graphDrag](https://github.com/zhysga/multi_agent_coope_with_graphDrag/tree/0440c9e83b7f5cccfa31807a846814c8d7d3a294) | `0440c9e83b7f5cccfa31807a846814c8d7d3a294` | 117 | MIT; license-text-collected; review-required |
| [jaguarkyng/langflow](https://github.com/jaguarkyng/langflow/tree/e26dff25be2a2d933ba70301ddadc026fa075fe0) | `e26dff25be2a2d933ba70301ddadc026fa075fe0` | 114 | MIT; license-text-collected; review-required |
| [prawin4E/langflow-hitl](https://github.com/prawin4E/langflow-hitl/tree/930b5b8d498fdeae39a1420e069feaf2775ac784) | `930b5b8d498fdeae39a1420e069feaf2775ac784` | 114 | MIT; license-text-collected; review-required |
| [cankanat/langflow](https://github.com/cankanat/langflow/tree/f2fb7b3b549dbd0582d4e0e629de97b39ba4b8cc) | `f2fb7b3b549dbd0582d4e0e629de97b39ba4b8cc` | 112 | MIT; license-text-collected; review-required |
| [haydonbawden/langflow](https://github.com/haydonbawden/langflow/tree/9fc6861aa83ae693e19f7339d922b8ad18dec561) | `9fc6861aa83ae693e19f7339d922b8ad18dec561` | 112 | MIT; license-text-collected; review-required |
| [arorakrishh/langflow-ai](https://github.com/arorakrishh/langflow-ai/tree/328d1b14ddb072a48bba42c1df7b5c61ca7d9d16) | `328d1b14ddb072a48bba42c1df7b5c61ca7d9d16` | 110 | unknown; unknown |
| [biyiyizuilihai/langflow](https://github.com/biyiyizuilihai/langflow/tree/f24a064baa4e698b1b9a92dc8c32ff13ad2e561b) | `f24a064baa4e698b1b9a92dc8c32ff13ad2e561b` | 109 | MIT; license-text-collected; review-required |
| [ILYESS24/langflow2.0](https://github.com/ILYESS24/langflow2.0/tree/1e6cfbf41cd8685d27e547149f4e8ba471734b97) | `1e6cfbf41cd8685d27e547149f4e8ba471734b97` | 76 | MIT; license-text-collected; review-required |
| [FelixFtch/SysML-AgentBench](https://github.com/FelixFtch/SysML-AgentBench/tree/0c4cfa785af97321a71c0934492793464777bc9f) | `0c4cfa785af97321a71c0934492793464777bc9f` | 62 | unknown; license-text-collected; review-required |
| [ACRT-EVAL/langflow-452-cr1](https://github.com/ACRT-EVAL/langflow-452-cr1/tree/3e6474b3480203c1da9728bf99ff76e08bf8c7be) | `3e6474b3480203c1da9728bf99ff76e08bf8c7be` | 60 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-452-cr10](https://github.com/ACRT-EVAL/langflow-452-cr10/tree/3e6474b3480203c1da9728bf99ff76e08bf8c7be) | `3e6474b3480203c1da9728bf99ff76e08bf8c7be` | 60 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-452-cr11](https://github.com/ACRT-EVAL/langflow-452-cr11/tree/3e6474b3480203c1da9728bf99ff76e08bf8c7be) | `3e6474b3480203c1da9728bf99ff76e08bf8c7be` | 60 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-452-cr5](https://github.com/ACRT-EVAL/langflow-452-cr5/tree/3e6474b3480203c1da9728bf99ff76e08bf8c7be) | `3e6474b3480203c1da9728bf99ff76e08bf8c7be` | 60 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-452-cr7](https://github.com/ACRT-EVAL/langflow-452-cr7/tree/3e6474b3480203c1da9728bf99ff76e08bf8c7be) | `3e6474b3480203c1da9728bf99ff76e08bf8c7be` | 60 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-452-cr9](https://github.com/ACRT-EVAL/langflow-452-cr9/tree/3e6474b3480203c1da9728bf99ff76e08bf8c7be) | `3e6474b3480203c1da9728bf99ff76e08bf8c7be` | 60 | MIT; license-text-collected; review-required |
| [Swetha-Selvaraj/langflow](https://github.com/Swetha-Selvaraj/langflow/tree/51cd807ab85c5a932b1fc8ca073755613b0ba976) | `51cd807ab85c5a932b1fc8ca073755613b0ba976` | 60 | MIT; license-text-collected; review-required |
| [sergiurt/langflow](https://github.com/sergiurt/langflow/tree/ee1b5494fc76268baeb133e0eb810ef9994e3b5e) | `ee1b5494fc76268baeb133e0eb810ef9994e3b5e` | 60 | MIT; license-text-collected; review-required |
| [vaishakhbn/langflow](https://github.com/vaishakhbn/langflow/tree/d73624e862775dde3b5a97b1bc0160447b93244a) | `d73624e862775dde3b5a97b1bc0160447b93244a` | 59 | MIT; license-text-collected; review-required |
| [AmokNepal/langflow](https://github.com/AmokNepal/langflow/tree/264681bf32a26ef6acf0f819559211e6d00578dc) | `264681bf32a26ef6acf0f819559211e6d00578dc` | 58 | MIT; license-text-collected; review-required |
| [cuttlely/cuttlely](https://github.com/cuttlely/cuttlely/tree/039379cb56471671f7838d4af7bc31fffcb2d9c3) | `039379cb56471671f7838d4af7bc31fffcb2d9c3` | 55 | Apache-2.0; license-text-collected; review-required |
| [JonasRigo/nima-semantica](https://github.com/JonasRigo/nima-semantica/tree/630f4e7ac978f1227b0d31d9a3327beb90f0b9d3) | `630f4e7ac978f1227b0d31d9a3327beb90f0b9d3` | 50 | MIT; license-text-collected; review-required |
| [David-codes0/langflow](https://github.com/David-codes0/langflow/tree/a3a950c290074385bfc38c9459ce838658b1ad92) | `a3a950c290074385bfc38c9459ce838658b1ad92` | 32 | MIT; license-text-collected; review-required |
| [cladius/agentic-ai](https://github.com/cladius/agentic-ai/tree/ba30e71d903b0960897f30ab387de6611828fb87) | `ba30e71d903b0960897f30ab387de6611828fb87` | 20 | MIT; license-text-collected; review-required |
| [mzeeshanaltaf/Langflow-Workflows](https://github.com/mzeeshanaltaf/Langflow-Workflows/tree/c042dd0cd014401acea3741e3c59d7a17ed1293b) | `c042dd0cd014401acea3741e3c59d7a17ed1293b` | 14 | MIT; license-text-collected; review-required |
| [DavidCatalano/agentic-playground-langflow](https://github.com/DavidCatalano/agentic-playground-langflow/tree/860d0139b1203bc06d5f515bb0a08e17ed91e664) | `860d0139b1203bc06d5f515bb0a08e17ed91e664` | 12 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-467-cr1](https://github.com/ACRT-EVAL/langflow-467-cr1/tree/9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1) | `9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1` | 11 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-467-cr10](https://github.com/ACRT-EVAL/langflow-467-cr10/tree/9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1) | `9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1` | 11 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-467-cr11](https://github.com/ACRT-EVAL/langflow-467-cr11/tree/9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1) | `9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1` | 11 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-467-cr5](https://github.com/ACRT-EVAL/langflow-467-cr5/tree/9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1) | `9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1` | 11 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-467-cr7](https://github.com/ACRT-EVAL/langflow-467-cr7/tree/9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1) | `9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1` | 11 | MIT; license-text-collected; review-required |
| [ACRT-EVAL/langflow-467-cr9](https://github.com/ACRT-EVAL/langflow-467-cr9/tree/9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1) | `9b3e4f27a54d4c2242f8f542a9eff3bba39ed9d1` | 11 | MIT; license-text-collected; review-required |
| [anima-kit/langflows](https://github.com/anima-kit/langflows/tree/a3452bb0b1aa51ba27190c40cf03f853135e7f48) | `a3452bb0b1aa51ba27190c40cf03f853135e7f48` | 11 | MIT; license-text-collected; review-required |
| [cfchase/langflow-examples](https://github.com/cfchase/langflow-examples/tree/8af07e4c7710a544287480c0180464cd63d846e7) | `8af07e4c7710a544287480c0180464cd63d846e7` | 11 | unknown; unknown |
| [neuronaut73/langflow2langgraph](https://github.com/neuronaut73/langflow2langgraph/tree/fcc0a61261c6937c9c4b38311c9b089dbfe09e4d) | `fcc0a61261c6937c9c4b38311c9b089dbfe09e4d` | 11 | unknown; unknown |
| [amit-timalsina/build-langflow-flows-using-ai](https://github.com/amit-timalsina/build-langflow-flows-using-ai/tree/c8142095f184c695783c91987fa4ed55cec50d2b) | `c8142095f184c695783c91987fa4ed55cec50d2b` | 9 | NOASSERTION; license-text-collected; review-required |
| [BibhuSundar/LangFlow](https://github.com/BibhuSundar/LangFlow/tree/c3d426ae5357f5352a7cf8a54b57f5ba4acdf61a) | `c3d426ae5357f5352a7cf8a54b57f5ba4acdf61a` | 8 | unknown; unknown |
| [Saptarshi767/Flowbit_orchestrator](https://github.com/Saptarshi767/Flowbit_orchestrator/tree/f95055c5069122e1e86fbee59a15bd74600fbca8) | `f95055c5069122e1e86fbee59a15bd74600fbca8` | 7 | unknown; unknown |
| [chauhan-Nirdosh/Langflow-AI-Playground](https://github.com/chauhan-Nirdosh/Langflow-AI-Playground/tree/df135b35909f85736dee32898fd1f5ce670d75ae) | `df135b35909f85736dee32898fd1f5ce670d75ae` | 7 | unknown; unknown |
| [ClemsAwels/langflow-flows](https://github.com/ClemsAwels/langflow-flows/tree/074945d42f4bd1046a0a7aa8db9abe6b2906cbca) | `074945d42f4bd1046a0a7aa8db9abe6b2906cbca` | 6 | unknown; unknown |
| [jkspeaks/LangFlow](https://github.com/jkspeaks/LangFlow/tree/cfd9264eb1a840dc642e091e9254ede6b5331a70) | `cfd9264eb1a840dc642e091e9254ede6b5331a70` | 6 | MIT; license-text-collected; review-required |
| [konradbjk/langflow-flows](https://github.com/konradbjk/langflow-flows/tree/39e606b8df424e2c7ded65e2dd5ecb29bdee8cc3) | `39e606b8df424e2c7ded65e2dd5ecb29bdee8cc3` | 6 | unknown; unknown |
| [SahilSapte11/Langflow_Data_Flows](https://github.com/SahilSapte11/Langflow_Data_Flows/tree/f2583920119bc2b11605e859196c1a532ecbfffa) | `f2583920119bc2b11605e859196c1a532ecbfffa` | 5 | unknown; unknown |
| [s1ds1ngh/Langflow-Workflows](https://github.com/s1ds1ngh/Langflow-Workflows/tree/5a2e358ec3e4a1cd4d5eff6e64f30cfadcb55671) | `5a2e358ec3e4a1cd4d5eff6e64f30cfadcb55671` | 5 | unknown; unknown |
| [xenon1919/LangFlow-Basic-Workflows](https://github.com/xenon1919/LangFlow-Basic-Workflows/tree/57303970a181d3d48c388558c7ae99ea99386660) | `57303970a181d3d48c388558c7ae99ea99386660` | 5 | unknown; unknown |
| [KIDA-BfR/LLM-agents_tutorial](https://github.com/KIDA-BfR/LLM-agents_tutorial/tree/ec34aa40e1a4f01988eaf91539f0ebb00a1df75f) | `ec34aa40e1a4f01988eaf91539f0ebb00a1df75f` | 4 | GPL-3.0; license-text-collected; review-required |
| [ifanzalukhu97/workshop-bwai-medan-2025](https://github.com/ifanzalukhu97/workshop-bwai-medan-2025/tree/9e39b81fc353d31cb9c0593f16d0d9d375e4baeb) | `9e39b81fc353d31cb9c0593f16d0d9d375e4baeb` | 4 | unknown; unknown |
| [jjvmr/langflow-ai-web-app](https://github.com/jjvmr/langflow-ai-web-app/tree/2d969e8e5bbc5fed12df0f31f78cbf08ca8dbbe0) | `2d969e8e5bbc5fed12df0f31f78cbf08ca8dbbe0` | 4 | unknown; unknown |
| [konradbjk/talk-building-genai-apps](https://github.com/konradbjk/talk-building-genai-apps/tree/a6c0fa9e5209bfbea4c8e8e5c74bd625ff3ab4fd) | `a6c0fa9e5209bfbea4c8e8e5c74bd625ff3ab4fd` | 4 | MIT; license-text-collected; review-required |
| [michelderu/watsonx-langflow-agent](https://github.com/michelderu/watsonx-langflow-agent/tree/9a6ce1945681905dc87e697c34a5e2dae1b5ee64) | `9a6ce1945681905dc87e697c34a5e2dae1b5ee64` | 4 | unknown; unknown |
| [nikolozGobejiShvili/langflow-project-flows](https://github.com/nikolozGobejiShvili/langflow-project-flows/tree/e501bfcf2ba345d11b5d8a946582796b036c6f04) | `e501bfcf2ba345d11b5d8a946582796b036c6f04` | 4 | unknown; unknown |
| [stevereiner/flexible-graphrag](https://github.com/stevereiner/flexible-graphrag/tree/8d58c671e7dcf02233fc1b2affcaa5829b2645fc) | `8d58c671e7dcf02233fc1b2affcaa5829b2645fc` | 4 | Apache-2.0; license-text-collected; review-required |
| [Hariharan232417/RAG_Implementation](https://github.com/Hariharan232417/RAG_Implementation/tree/2f415cae78be41aebcc5c306b6cba836fc4e67e8) | `2f415cae78be41aebcc5c306b6cba836fc4e67e8` | 3 | unknown; unknown |
| [KindTechUK/langflow-prototype-examples](https://github.com/KindTechUK/langflow-prototype-examples/tree/4c621a8b6ece33d0a68d9dcc6db4b4219da0dcd8) | `4c621a8b6ece33d0a68d9dcc6db4b4219da0dcd8` | 3 | MIT; license-text-collected; review-required |
| [NithiyaKS/RAG-Langflow](https://github.com/NithiyaKS/RAG-Langflow/tree/c9468c629693905ed084fd042978e97dbabba2cd) | `c9468c629693905ed084fd042978e97dbabba2cd` | 3 | unknown; unknown |
| [Optimal-Living-Systems/deepflo](https://github.com/Optimal-Living-Systems/deepflo/tree/5bc6c097738849d7d1cd07d82c64f75b225ff48d) | `5bc6c097738849d7d1cd07d82c64f75b225ff48d` | 3 | NOASSERTION; license-text-collected; review-required |
| [Sneha-Ms/Langflow-Project](https://github.com/Sneha-Ms/Langflow-Project/tree/ab58a2bf1f9b00bb51370c60656571f631e9f45e) | `ab58a2bf1f9b00bb51370c60656571f631e9f45e` | 3 | unknown; unknown |
| [TobiasSMann/LangFlow_Templates](https://github.com/TobiasSMann/LangFlow_Templates/tree/f440cf549d56f4343a93d42b93fd7853f629d230) | `f440cf549d56f4343a93d42b93fd7853f629d230` | 3 | unknown; unknown |
| [Yangjon1/llmworkflow](https://github.com/Yangjon1/llmworkflow/tree/5912b94e20a0e99382879e72066bca5531bbe5ea) | `5912b94e20a0e99382879e72066bca5531bbe5ea` | 3 | MIT; license-text-collected; review-required |
| [bhaumikgohel/Langflow_Workflow](https://github.com/bhaumikgohel/Langflow_Workflow/tree/39a2e10b9eaa257c042bcd55d8dec92eca565da7) | `39a2e10b9eaa257c042bcd55d8dec92eca565da7` | 3 | unknown; unknown |
| [datastaxdevs/ai-evaluation-langflow-phoenix](https://github.com/datastaxdevs/ai-evaluation-langflow-phoenix/tree/beb45cdf8a6c5d301b89f22ac2ec97f9b85ea294) | `beb45cdf8a6c5d301b89f22ac2ec97f9b85ea294` | 3 | unknown; unknown |
| [krakenalt/langflow_examples](https://github.com/krakenalt/langflow_examples/tree/5a5dac8ce91a4ca5f71db5c42a7e8f400807af98) | `5a5dac8ce91a4ca5f71db5c42a7e8f400807af98` | 3 | unknown; unknown |
| [michelderu/agentic-ai-workshop](https://github.com/michelderu/agentic-ai-workshop/tree/2b6796f459c5d041c6e8025e73e4220bbad63df3) | `2b6796f459c5d041c6e8025e73e4220bbad63df3` | 3 | unknown; unknown |
| [nanosep/langflow-projects](https://github.com/nanosep/langflow-projects/tree/928a17b7be70906b86273913118b580c2d18391a) | `928a17b7be70906b86273913118b580c2d18391a` | 3 | unknown; unknown |
| [nchanduka/langflow-flows](https://github.com/nchanduka/langflow-flows/tree/ba6836a7d3edb31c7c4cf8930851cb0cd45b58b1) | `ba6836a7d3edb31c7c4cf8930851cb0cd45b58b1` | 3 | unknown; unknown |
| [nicoloboschi/langflow-flows](https://github.com/nicoloboschi/langflow-flows/tree/2a84dc23111725c3c77125e1b51a6429c912e1da) | `2a84dc23111725c3c77125e1b51a6429c912e1da` | 3 | MIT; license-text-collected; review-required |
| [poojaqa-123/AI_TESTER_3X](https://github.com/poojaqa-123/AI_TESTER_3X/tree/dfe947208c57f1cbf172ba220597feec5aa2d416) | `dfe947208c57f1cbf172ba220597feec5aa2d416` | 3 | unknown; unknown |
| [sergey-kasatov/arkon-manufacturing-ai](https://github.com/sergey-kasatov/arkon-manufacturing-ai/tree/8f3fb57014adf9d0bbeb7c11380fd03237832f3c) | `8f3fb57014adf9d0bbeb7c11380fd03237832f3c` | 3 | MIT; license-text-collected; review-required |
| [smatiolids/trybe-ai-agents-workshop](https://github.com/smatiolids/trybe-ai-agents-workshop/tree/b3e5adf718d4c09a24d321e1c0680487f1349387) | `b3e5adf718d4c09a24d321e1c0680487f1349387` | 3 | unknown; unknown |
| [yaitec/yaitec-hub-templates](https://github.com/yaitec/yaitec-hub-templates/tree/512afe2129e525c435177339f5f33a8dc93b1c21) | `512afe2129e525c435177339f5f33a8dc93b1c21` | 3 | MIT; license-text-collected; review-required |
| [Aashay30/Multi_Agent_App](https://github.com/Aashay30/Multi_Agent_App/tree/d7c45f51188f016965540ed212f556680f000d86) | `d7c45f51188f016965540ed212f556680f000d86` | 2 | unknown; unknown |
| [Abdul-Muizz1310/LangFlow-Financial-RAG-Chatbot](https://github.com/Abdul-Muizz1310/LangFlow-Financial-RAG-Chatbot/tree/a03ba1a5c1d62f4c49bb58eabe7767f5e097ac4f) | `a03ba1a5c1d62f4c49bb58eabe7767f5e097ac4f` | 2 | unknown; unknown |
| [AbhinavK1705/AI-Driven_Adaptive_Server_Cooling](https://github.com/AbhinavK1705/AI-Driven_Adaptive_Server_Cooling/tree/3f1fc8807b8e7fc23fcf554858385c42d3f53f38) | `3f1fc8807b8e7fc23fcf554858385c42d3f53f38` | 2 | unknown; unknown |
| [Aditya066/LangflowRAGPipeline](https://github.com/Aditya066/LangflowRAGPipeline/tree/eeb2b92c7909b1c9c9ca196670f36c8577456a40) | `eeb2b92c7909b1c9c9ca196670f36c8577456a40` | 2 | unknown; unknown |
| [Akhil-Anupoju/AI-Powered-Multi-Agent-Workout-Assistant](https://github.com/Akhil-Anupoju/AI-Powered-Multi-Agent-Workout-Assistant/tree/2badc226bae12eae601d90e626f645ee3441097b) | `2badc226bae12eae601d90e626f645ee3441097b` | 2 | unknown; unknown |
| [AmberForrester/menocare](https://github.com/AmberForrester/menocare/tree/00b487dc9dd0bf33754989e64334f90fcfe0dce7) | `00b487dc9dd0bf33754989e64334f90fcfe0dce7` | 2 | unknown; unknown |
| [Aryan1623/Socio2](https://github.com/Aryan1623/Socio2/tree/a3366f491585b125e5e338f9ed2c955927f230c1) | `a3366f491585b125e5e338f9ed2c955927f230c1` | 2 | unknown; unknown |
| [DisantHoridnt/langflow-hf-agents-demo](https://github.com/DisantHoridnt/langflow-hf-agents-demo/tree/807cee2c21dda4db6466be6c06f20354868ef06b) | `807cee2c21dda4db6466be6c06f20354868ef06b` | 2 | unknown; unknown |
| [GANESH-MAHARAJ/Yantra-Adaptive-Server-Cooling](https://github.com/GANESH-MAHARAJ/Yantra-Adaptive-Server-Cooling/tree/1b47f6c4df166d7effc5f586ef5090524489624d) | `1b47f6c4df166d7effc5f586ef5090524489624d` | 2 | unknown; unknown |
| [LoserLLM/LangFlow-Files](https://github.com/LoserLLM/LangFlow-Files/tree/2fed5e20a85d2b57e2a7015057802b8b3609eb70) | `2fed5e20a85d2b57e2a7015057802b8b3609eb70` | 2 | MIT; license-text-collected; review-required |
| [PREMRAJESH/RAG](https://github.com/PREMRAJESH/RAG/tree/654ba55fcebc7903cbabf4b463767f8568431058) | `654ba55fcebc7903cbabf4b463767f8568431058` | 2 | MIT; license-text-collected; review-required |
| [PrajwalNAW/AI-Agent-with-Langflow](https://github.com/PrajwalNAW/AI-Agent-with-Langflow/tree/f7a7e651f1e80c0eb30e606a0101ca43e93e01a3) | `f7a7e651f1e80c0eb30e606a0101ca43e93e01a3` | 2 | unknown; unknown |
| [ProDocs/langflow-adb-mcp-starter](https://github.com/ProDocs/langflow-adb-mcp-starter/tree/58f4b886d9e331490bd3963e60eee00ceb8f784a) | `58f4b886d9e331490bd3963e60eee00ceb8f784a` | 2 | MIT; license-text-collected; review-required |
| [TMoneyBidness/langflow_examples](https://github.com/TMoneyBidness/langflow_examples/tree/5f12815875ac75493e389c601d57bba69d5e3944) | `5f12815875ac75493e389c601d57bba69d5e3944` | 2 | MIT; license-text-collected; review-required |
| [akshay076/SwiftStart](https://github.com/akshay076/SwiftStart/tree/f3ed5f1d2feea589ab648afd4e0e8e24b547f067) | `f3ed5f1d2feea589ab648afd4e0e8e24b547f067` | 2 | unknown; license-text-collected; review-required |
| [bappichok/AI_Agents_Langflow_json_file](https://github.com/bappichok/AI_Agents_Langflow_json_file/tree/44e33493aa9651d0e0f58b1313cee1e709314140) | `44e33493aa9651d0e0f58b1313cee1e709314140` | 2 | unknown; unknown |
| [beprith/OT-Service-Support-Assistant](https://github.com/beprith/OT-Service-Support-Assistant/tree/905eab9fa8903723bb11b76a512a8ce545ade939) | `905eab9fa8903723bb11b76a512a8ce545ade939` | 2 | MIT; license-text-collected; review-required |
| [datastaxdevs/build_accurate_ai_langflow_arize](https://github.com/datastaxdevs/build_accurate_ai_langflow_arize/tree/d30e9f15fd0693676d48fa5dddd2030421774a10) | `d30e9f15fd0693676d48fa5dddd2030421774a10` | 2 | unknown; unknown |
| [devinaumies/Langflow-Project](https://github.com/devinaumies/Langflow-Project/tree/157133cf89775637cecc1e3456f611b0cbbfa338) | `157133cf89775637cecc1e3456f611b0cbbfa338` | 2 | unknown; unknown |
| [durbun-digital/langflow-integration](https://github.com/durbun-digital/langflow-integration/tree/44f125230bd0733155fe42cde0c38f3769b04e35) | `44f125230bd0733155fe42cde0c38f3769b04e35` | 2 | NOASSERTION; license-text-collected; review-required |
| [fearyan/Trainerr](https://github.com/fearyan/Trainerr/tree/8fff2935fa47e34a0ad67794a31e5a10982624f9) | `8fff2935fa47e34a0ad67794a31e5a10982624f9` | 2 | MIT; license-text-collected; review-required |
| [gorodulin/last_summer_agent](https://github.com/gorodulin/last_summer_agent/tree/7176b679df3bc28309c8c4a2e34d3ea1b19aee3d) | `7176b679df3bc28309c8c4a2e34d3ea1b19aee3d` | 2 | unknown; unknown |
| [izztshfq/kd-langflow-examples](https://github.com/izztshfq/kd-langflow-examples/tree/6e7e6e5ac40138c6bef64833bf1b23772a247356) | `6e7e6e5ac40138c6bef64833bf1b23772a247356` | 2 | unknown; unknown |
| [manoharkamarushi/QA_Agents_Langflow](https://github.com/manoharkamarushi/QA_Agents_Langflow/tree/137b56c6eae020d9dd22c0f6a3efdf8e88e35ba8) | `137b56c6eae020d9dd22c0f6a3efdf8e88e35ba8` | 2 | unknown; unknown |
| [mathematica-ai/flowkit](https://github.com/mathematica-ai/flowkit/tree/fd2b64654864121172b4adb0e618b06c911e7095) | `fd2b64654864121172b4adb0e618b06c911e7095` | 2 | Apache-2.0; license-text-collected; review-required |
| [mzeeshanaltaf/langflow-image-generation](https://github.com/mzeeshanaltaf/langflow-image-generation/tree/f35e8e09179c63afa67993d4eaeeb00d4d80660b) | `f35e8e09179c63afa67993d4eaeeb00d4d80660b` | 2 | unknown; unknown |
| [mzeeshanaltaf/langflow-video-generation](https://github.com/mzeeshanaltaf/langflow-video-generation/tree/f53ca25bd89e5bbda7991d63f974130136174107) | `f53ca25bd89e5bbda7991d63f974130136174107` | 2 | Apache-2.0; license-text-collected; review-required |
| [namastexlabs/automagik-spark](https://github.com/namastexlabs/automagik-spark/tree/dac2ba2008c4a6f4117b70ba17c5c2f9d0f4fd65) | `dac2ba2008c4a6f4117b70ba17c5c2f9d0f4fd65` | 2 | MIT; license-text-collected; review-required |
| [pataballapravallika/Advanced-Multi-Agent-Workout-App](https://github.com/pataballapravallika/Advanced-Multi-Agent-Workout-App/tree/2073ddbd1e59d706141394b9dd72903c09dad1f4) | `2073ddbd1e59d706141394b9dd72903c09dad1f4` | 2 | unknown; unknown |
| [paulomuraroferreira/langflow_ragas](https://github.com/paulomuraroferreira/langflow_ragas/tree/2c15878e41905945e2e40a4a7ac42e9c57f3ceb4) | `2c15878e41905945e2e40a4a7ac42e9c57f3ceb4` | 2 | unknown; unknown |
| [qife422/ai-review-console](https://github.com/qife422/ai-review-console/tree/aefb10edc7ce001823803d13018955c03d580cca) | `aefb10edc7ce001823803d13018955c03d580cca` | 2 | Apache-2.0; license-text-collected; review-required |
| [sammyhu-Dec/RAG-langflow](https://github.com/sammyhu-Dec/RAG-langflow/tree/8ff28dcf798b99b269adf3eaaf589e03bcde79c6) | `8ff28dcf798b99b269adf3eaaf589e03bcde79c6` | 2 | unknown; unknown |
| [sefzig/langflow-translation](https://github.com/sefzig/langflow-translation/tree/ac7b6d867fbad1921f9493f2fd9208f0e640b169) | `ac7b6d867fbad1921f9493f2fd9208f0e640b169` | 2 | unknown; unknown |
| [smatiolids/airline-ai-agent](https://github.com/smatiolids/airline-ai-agent/tree/65055b923946931256375de91f26dc3d6f0c4143) | `65055b923946931256375de91f26dc3d6f0c4143` | 2 | unknown; unknown |
| [smatiolids/langflow-code-integrity](https://github.com/smatiolids/langflow-code-integrity/tree/f602f80e07b72cefcb94d46727d691951af4d334) | `f602f80e07b72cefcb94d46727d691951af4d334` | 2 | unknown; unknown |
| [AkshatBhat/Langflow-Customer-Support-Agent](https://github.com/AkshatBhat/Langflow-Customer-Support-Agent/tree/b909d8c5f66e2e53fffe7479e136449c557ab512) | `b909d8c5f66e2e53fffe7479e136449c557ab512` | 1 | MIT; license-text-collected; review-required |
| [AkshatThecoder/Langflow_tutorial](https://github.com/AkshatThecoder/Langflow_tutorial/tree/93930192771557ab58fb27aa6a085d0614206279) | `93930192771557ab58fb27aa6a085d0614206279` | 1 | unknown; unknown |
| [AmarirNaima/RAG-Langflow](https://github.com/AmarirNaima/RAG-Langflow/tree/fe246b449d21c73b2f73b2465ba9d088cae7a7cf) | `fe246b449d21c73b2f73b2465ba9d088cae7a7cf` | 1 | unknown; unknown |
| [AntQua/Customer-Support-AI-Agent](https://github.com/AntQua/Customer-Support-AI-Agent/tree/49a701a6ab30111c506c77f9a5af44b7de0e3661) | `49a701a6ab30111c506c77f9a5af44b7de0e3661` | 1 | MIT; license-text-collected; review-required |
| [AperionAI/shield-langflow](https://github.com/AperionAI/shield-langflow/tree/9d405d8be8997212247a59f60042dc2ea59faa2c) | `9d405d8be8997212247a59f60042dc2ea59faa2c` | 1 | Apache-2.0; license-text-collected; review-required |
| [ArchDevData/langflowRAG1](https://github.com/ArchDevData/langflowRAG1/tree/41e3e38cb068e6040faf4868e50a77fbcd6e3dc6) | `41e3e38cb068e6040faf4868e50a77fbcd6e3dc6` | 1 | unknown; unknown |
| [Argha9851/audio-signal-processing-assistant-agent](https://github.com/Argha9851/audio-signal-processing-assistant-agent/tree/467942e1ed2d10c080e5d4a1a4b89f3b19e85b08) | `467942e1ed2d10c080e5d4a1a4b89f3b19e85b08` | 1 | unknown; unknown |
| [Barabacha474/Thesis-RAG-LLM](https://github.com/Barabacha474/Thesis-RAG-LLM/tree/216e5a608378ba3b27aaed3a4d90020b4486ebe0) | `216e5a608378ba3b27aaed3a4d90020b4486ebe0` | 1 | unknown; unknown |
| [Biplab77/LangFlow](https://github.com/Biplab77/LangFlow/tree/eae64ca9d0fd695d6cf4c4d0aa5bc20fa9587674) | `eae64ca9d0fd695d6cf4c4d0aa5bc20fa9587674` | 1 | unknown; unknown |
| [CauanDZN/enhanced_obsidian](https://github.com/CauanDZN/enhanced_obsidian/tree/9c92dc1f6853a1cf2598a40d9f502d3f78e4c5fe) | `9c92dc1f6853a1cf2598a40d9f502d3f78e4c5fe` | 1 | unknown; unknown |
| [Codex-Amit/interview-trainer-chatbot](https://github.com/Codex-Amit/interview-trainer-chatbot/tree/a63b3639f90cbbd3ed1a436fd6e24c7e841ce616) | `a63b3639f90cbbd3ed1a436fd6e24c7e841ce616` | 1 | MIT; license-text-collected; review-required |
| [DaffaWiratama/RAG-Project-for-IBMSkillsbuild-Capstone](https://github.com/DaffaWiratama/RAG-Project-for-IBMSkillsbuild-Capstone/tree/2e19f815593bce6321ccf39c77b31d9d16976482) | `2e19f815593bce6321ccf39c77b31d9d16976482` | 1 | unknown; unknown |
| [Dhruv0038/CUSTOMERCONSULTANCYWEBAPP](https://github.com/Dhruv0038/CUSTOMERCONSULTANCYWEBAPP/tree/07a33cb9e8795223b93a310c9d159d4bc1e2d918) | `07a33cb9e8795223b93a310c9d159d4bc1e2d918` | 1 | unknown; unknown |
| [Digitalspy12/SocialMedia_analyst_LevelSupermind-Hackathon_2024](https://github.com/Digitalspy12/SocialMedia_analyst_LevelSupermind-Hackathon_2024/tree/43a66d9a4864625376836e7abf8e7b0efc57d4fa) | `43a66d9a4864625376836e7abf8e7b0efc57d4fa` | 1 | unknown; unknown |
| [DonGuillotine/content-smith-ai](https://github.com/DonGuillotine/content-smith-ai/tree/059e5b11eaedfa464eca1fb8ca59a2c939c8d1c6) | `059e5b11eaedfa464eca1fb8ca59a2c939c8d1c6` | 1 | unknown; unknown |
| [EdgeAgent/visionary3d-studio](https://github.com/EdgeAgent/visionary3d-studio/tree/e1b0f99533616079a37c1c53998aac63231cfd49) | `e1b0f99533616079a37c1c53998aac63231cfd49` | 1 | MIT; license-text-collected; review-required |
| [Elirianne/ai-agents-langflow](https://github.com/Elirianne/ai-agents-langflow/tree/8a79efb0b237b1fd4d2a76028e74aeb791660895) | `8a79efb0b237b1fd4d2a76028e74aeb791660895` | 1 | unknown; unknown |
| [HarinathAnnavarapu/RAG-IngestionAndRetrieval-Impl](https://github.com/HarinathAnnavarapu/RAG-IngestionAndRetrieval-Impl/tree/5979ae887f8d9b7961295b8c165e3cd3ef32e7db) | `5979ae887f8d9b7961295b8c165e3cd3ef32e7db` | 1 | unknown; unknown |
| [HasanSafa/Langflow-Practical-Challenge-Project](https://github.com/HasanSafa/Langflow-Practical-Challenge-Project/tree/ec02055b465d36e93a4ed26fe1cc88067ba048df) | `ec02055b465d36e93a4ed26fe1cc88067ba048df` | 1 | unknown; unknown |
| [KarthikChekuri/Personal-RAG](https://github.com/KarthikChekuri/Personal-RAG/tree/0974dbb213692cd513cdb362d13d480d35d8f758) | `0974dbb213692cd513cdb362d13d480d35d8f758` | 1 | unknown; unknown |
| [KartikKarakoti/Langflow_Pest_and_Disease_Detection_Agent_Project](https://github.com/KartikKarakoti/Langflow_Pest_and_Disease_Detection_Agent_Project/tree/c87c4b53fd13ab53e63290dd3d8a0a850d4c89c7) | `c87c4b53fd13ab53e63290dd3d8a0a850d4c89c7` | 1 | unknown; unknown |
| [MJCappella/MultiAgent-Workout-App](https://github.com/MJCappella/MultiAgent-Workout-App/tree/95a7ba7dd5681974f6795ef73586f9d681487603) | `95a7ba7dd5681974f6795ef73586f9d681487603` | 1 | unknown; unknown |
| [Manjusha3010/naive-rag-langflow](https://github.com/Manjusha3010/naive-rag-langflow/tree/d362cb45c7a4695e2e029bee0f1c8ad4c0dbcf18) | `d362cb45c7a4695e2e029bee0f1c8ad4c0dbcf18` | 1 | unknown; unknown |
| [MariaaWaheed/ReadAid.ai](https://github.com/MariaaWaheed/ReadAid.ai/tree/f418880f79a2d71940de15dd825d81f6372e7cd1) | `f418880f79a2d71940de15dd825d81f6372e7cd1` | 1 | unknown; unknown |
| [NavodPeiris/github_repo_rag_langflow](https://github.com/NavodPeiris/github_repo_rag_langflow/tree/95b6b486b52a7e1b2dcfacdfc0d716f9e9ece938) | `95b6b486b52a7e1b2dcfacdfc0d716f9e9ece938` | 1 | MIT; license-text-collected; review-required |
| [NeVarliki/Varlik-Langflow-AI](https://github.com/NeVarliki/Varlik-Langflow-AI/tree/51a4573f699d4561eef5e6a94e4f52078504fdd3) | `51a4573f699d4561eef5e6a94e4f52078504fdd3` | 1 | unknown; unknown |
| [OUANZOUGUIAbdelhak/ARTICLE-VALIDATION-LANGFLOW-WORKFLOW](https://github.com/OUANZOUGUIAbdelhak/ARTICLE-VALIDATION-LANGFLOW-WORKFLOW/tree/5d534ca344f19144bc57e4e798f878b5e32282c5) | `5d534ca344f19144bc57e4e798f878b5e32282c5` | 1 | unknown; unknown |
| [QaimMehdi/Adaptive-Multi-Format-RAG-System-with-Langflow-Chroma-DB](https://github.com/QaimMehdi/Adaptive-Multi-Format-RAG-System-with-Langflow-Chroma-DB/tree/728888e016c1caf382fc2d5493d044d37505c411) | `728888e016c1caf382fc2d5493d044d37505c411` | 1 | unknown; unknown |
| [RHKOLTE/LangFlowTest](https://github.com/RHKOLTE/LangFlowTest/tree/56fdd238bfb2ea68c6b642f107872a2bcd624b7c) | `56fdd238bfb2ea68c6b642f107872a2bcd624b7c` | 1 | unknown; unknown |
| [Rishirajbal/Langflow_Workflows](https://github.com/Rishirajbal/Langflow_Workflows/tree/80b9a009f1ebcf183db2fb032e09ce7484104995) | `80b9a009f1ebcf183db2fb032e09ce7484104995` | 1 | unknown; unknown |
| [Rohaz-bhalla/LangFlow-Workflows](https://github.com/Rohaz-bhalla/LangFlow-Workflows/tree/be7b707d61b5e583cbf73b7c837faf6ea4d9241e) | `be7b707d61b5e583cbf73b7c837faf6ea4d9241e` | 1 | MIT; license-text-collected; review-required |
| [RonnieAI/LangflowTutorial](https://github.com/RonnieAI/LangflowTutorial/tree/5903082371a7ccc2e254baa829deaf51b0db0165) | `5903082371a7ccc2e254baa829deaf51b0db0165` | 1 | unknown; unknown |
| [RuchirS-spec/Courtroom-Clash](https://github.com/RuchirS-spec/Courtroom-Clash/tree/9ecd8b6267df4b749453335c9b83c5d972e86101) | `9ecd8b6267df4b749453335c9b83c5d972e86101` | 1 | unknown; unknown |
| [Rudra1402/Langflow](https://github.com/Rudra1402/Langflow/tree/2cda628a66c85e121ff2c586911d240c54faedcd) | `2cda628a66c85e121ff2c586911d240c54faedcd` | 1 | unknown; unknown |
| [Rushikagundu/RAGBasedAopplicationUsingLangflow](https://github.com/Rushikagundu/RAGBasedAopplicationUsingLangflow/tree/fe02e7523d5026a24a7c9576f77070b93231ccf7) | `fe02e7523d5026a24a7c9576f77070b93231ccf7` | 1 | unknown; unknown |
| [RyvrImmersive/langflow-runner](https://github.com/RyvrImmersive/langflow-runner/tree/0b42406397c45450153241056e67f91d44d1db64) | `0b42406397c45450153241056e67f91d44d1db64` | 1 | unknown; unknown |
| [Saleha198/Criminal-Law-Agent](https://github.com/Saleha198/Criminal-Law-Agent/tree/793e13436690b4b0f1fc06a4b92caa12951d6d1b) | `793e13436690b4b0f1fc06a4b92caa12951d6d1b` | 1 | unknown; unknown |
| [Saurabh-shell4future/College-Admission-Agent-RAG](https://github.com/Saurabh-shell4future/College-Admission-Agent-RAG/tree/c4f9c5ab9f6f24391225d961c8e33e821dd78d03) | `c4f9c5ab9f6f24391225d961c8e33e821dd78d03` | 1 | unknown; unknown |
| [Sharathchenna/EngageMetrics](https://github.com/Sharathchenna/EngageMetrics/tree/01a2991d24df10a04c1ce53aef8c6b64c146ecd3) | `01a2991d24df10a04c1ce53aef8c6b64c146ecd3` | 1 | unknown; unknown |
| [Shivsrijit/FitGenius](https://github.com/Shivsrijit/FitGenius/tree/7d9295a9ddcecf50fe63c1ebb05474312303dae0) | `7d9295a9ddcecf50fe63c1ebb05474312303dae0` | 1 | unknown; unknown |
| [Shonty10/usf-advising-agent](https://github.com/Shonty10/usf-advising-agent/tree/fac2e03478dbca508b602752f19bb6ba6f3b5b8e) | `fac2e03478dbca508b602752f19bb6ba6f3b5b8e` | 1 | MIT; license-text-collected; review-required |
| [Shray12-PM/ai-multi-agent-orchestration-langflow](https://github.com/Shray12-PM/ai-multi-agent-orchestration-langflow/tree/5d716fe60c8686924110ece9eee964e5ecd8a2fc) | `5d716fe60c8686924110ece9eee964e5ecd8a2fc` | 1 | NOASSERTION; license-text-collected; review-required |
| [Sonteru4/multi-agent-customer-support](https://github.com/Sonteru4/multi-agent-customer-support/tree/c0d310d57528ce27e34762784b8020bfb496d0e4) | `c0d310d57528ce27e34762784b8020bfb496d0e4` | 1 | unknown; unknown |
| [TejasS13/multi-agent-deep-researcher](https://github.com/TejasS13/multi-agent-deep-researcher/tree/970c5729f7b73d027b31e02994544ea91b746ab5) | `970c5729f7b73d027b31e02994544ea91b746ab5` | 1 | unknown; unknown |
| [Vinayaks439/LangFlow-MCP-High-ATS-Resume-creator](https://github.com/Vinayaks439/LangFlow-MCP-High-ATS-Resume-creator/tree/95bf4b1733bcaec6f805b383a285668b846ccf05) | `95bf4b1733bcaec6f805b383a285668b846ccf05` | 1 | unknown; unknown |
| [Yalnegheimish/nl-sql-json-pdf-report-challenge](https://github.com/Yalnegheimish/nl-sql-json-pdf-report-challenge/tree/43d6b30883fb296db3cc504491d84ffdeda8610d) | `43d6b30883fb296db3cc504491d84ffdeda8610d` | 1 | unknown; unknown |
| [YogeshvarM/RAG-and-Agents-using-Langflow](https://github.com/YogeshvarM/RAG-and-Agents-using-Langflow/tree/87471b13ba86fcae5af571d71c4ccff54a12fa10) | `87471b13ba86fcae5af571d71c4ccff54a12fa10` | 1 | unknown; unknown |
| [adhityan924/DoorDashAgent](https://github.com/adhityan924/DoorDashAgent/tree/7d9549c3f5e55853bd789548d77ca685a8ebc3d7) | `7d9549c3f5e55853bd789548d77ca685a8ebc3d7` | 1 | unknown; unknown |
| [ai-bites/simple-rag-app](https://github.com/ai-bites/simple-rag-app/tree/8eee648fb17e6dce85c48a9c0e7826ba09aff67b) | `8eee648fb17e6dce85c48a9c0e7826ba09aff67b` | 1 | unknown; unknown |
| [akariKito098/pi_pilot_langflow](https://github.com/akariKito098/pi_pilot_langflow/tree/5e3fa9c99600275b129faaad77f2b6fdff52ce5f) | `5e3fa9c99600275b129faaad77f2b6fdff52ce5f` | 1 | unknown; unknown |
| [akhil838/RAG](https://github.com/akhil838/RAG/tree/a9fb56a9da573d589d7a842fd3cd8fce5274ff27) | `a9fb56a9da573d589d7a842fd3cd8fce5274ff27` | 1 | unknown; unknown |
| [alexhuang-dev/assembly-optimizer-system](https://github.com/alexhuang-dev/assembly-optimizer-system/tree/4c1175c6770017875e34702293dc63e60bb1bbc2) | `4c1175c6770017875e34702293dc63e60bb1bbc2` | 1 | Apache-2.0; license-text-collected; review-required |
| [avimallick/Cobol-to-Python](https://github.com/avimallick/Cobol-to-Python/tree/d18bf0d0ae6caccc59f5087b51a1b5825e848e64) | `d18bf0d0ae6caccc59f5087b51a1b5825e848e64` | 1 | MIT; license-text-collected; review-required |
| [baraksharon/jeen-langflow-agents](https://github.com/baraksharon/jeen-langflow-agents/tree/74e0cfbff727c352b184250e38e53be26bdfef93) | `74e0cfbff727c352b184250e38e53be26bdfef93` | 1 | unknown; unknown |
| [beprith/CityInsights_TelegramBot](https://github.com/beprith/CityInsights_TelegramBot/tree/d1342c68d3bfbba8ef0027dd05577b58fc87e277) | `d1342c68d3bfbba8ef0027dd05577b58fc87e277` | 1 | MIT; license-text-collected; review-required |
| [betloreilly/RAG_with_Analytics-Watsonxdata_Unstructured_Langflow](https://github.com/betloreilly/RAG_with_Analytics-Watsonxdata_Unstructured_Langflow/tree/a6dd82751d7d7907552a37b12c0737d803233aa6) | `a6dd82751d7d7907552a37b12c0737d803233aa6` | 1 | unknown; unknown |
| [contantuser02/EcoGuard-Golden-Corridor](https://github.com/contantuser02/EcoGuard-Golden-Corridor/tree/44e69f80b0758aa7088f9f8a2eaf31475ae2017e) | `44e69f80b0758aa7088f9f8a2eaf31475ae2017e` | 1 | unknown; unknown |
| [costaalan/sprint-health-agent](https://github.com/costaalan/sprint-health-agent/tree/9d4b86c93cc866a852f2db2ae865f4a2a3cb78db) | `9d4b86c93cc866a852f2db2ae865f4a2a3cb78db` | 1 | unknown; unknown |
| [danielgblanco/dangb-langflow](https://github.com/danielgblanco/dangb-langflow/tree/61c2da4e3925c3307aa11f1985d64da9968aedc8) | `61c2da4e3925c3307aa11f1985d64da9968aedc8` | 1 | Apache-2.0; license-text-collected; review-required |
| [darshandugar2004/Low-Code-No-Code-Langflow](https://github.com/darshandugar2004/Low-Code-No-Code-Langflow/tree/1c0d9d75501f073735ad9b9b2e75ba44efdd04e9) | `1c0d9d75501f073735ad9b9b2e75ba44efdd04e9` | 1 | unknown; unknown |
| [datastax/search-accuracy-demo](https://github.com/datastax/search-accuracy-demo/tree/b3ebfb960594f8092034ad55c153e7a913022027) | `b3ebfb960594f8092034ad55c153e7a913022027` | 1 | unknown; unknown |
| [datavilleorg/langflow-company-research](https://github.com/datavilleorg/langflow-company-research/tree/7640a7443b5ecea17aa62f4f32ace432fc4c2fcd) | `7640a7443b5ecea17aa62f4f32ace432fc4c2fcd` | 1 | MIT; license-text-collected; review-required |
| [deepanshBatra/RAG-Langflow](https://github.com/deepanshBatra/RAG-Langflow/tree/3be5cf4450320723639a9398f881ae1cc3fff4e3) | `3be5cf4450320723639a9398f881ae1cc3fff4e3` | 1 | unknown; unknown |
| [dikshahahas/Doc_STRICT_FAQbot](https://github.com/dikshahahas/Doc_STRICT_FAQbot/tree/4924cd148e0a9cac207052adf91737d49c43c3f9) | `4924cd148e0a9cac207052adf91737d49c43c3f9` | 1 | unknown; unknown |
| [eyuuab/AI_Agents_Workflows](https://github.com/eyuuab/AI_Agents_Workflows/tree/46d35b3e28d4dbc8ee17a14e13ff510fd2a49b22) | `46d35b3e28d4dbc8ee17a14e13ff510fd2a49b22` | 1 | unknown; unknown |
| [fabiojrbraga/competicao_langflow_RAG](https://github.com/fabiojrbraga/competicao_langflow_RAG/tree/eecfd1c105816f130d10c907f7858ee088a4e63f) | `eecfd1c105816f130d10c907f7858ee088a4e63f` | 1 | unknown; unknown |
| [fbercken/langflow-examples](https://github.com/fbercken/langflow-examples/tree/cd4fc7513f4c47fedb92dc9dec7547975ed1b7fb) | `cd4fc7513f4c47fedb92dc9dec7547975ed1b7fb` | 1 | unknown; unknown |
| [gaurav122427/Language-tutor-langflow](https://github.com/gaurav122427/Language-tutor-langflow/tree/5f1fc4640f38ee3962cfd91f9b02fd58142fa68c) | `5f1fc4640f38ee3962cfd91f9b02fd58142fa68c` | 1 | MIT; license-text-collected; review-required |
| [giorgos153/RagProjectLangflow](https://github.com/giorgos153/RagProjectLangflow/tree/4368d7895155177060d22f07039cc1a87960b18b) | `4368d7895155177060d22f07039cc1a87960b18b` | 1 | unknown; unknown |
| [gugulothubhavith/AI-Educational-Admission-Assistant](https://github.com/gugulothubhavith/AI-Educational-Admission-Assistant/tree/6502a615357ea13ef9d2952321794216f86b268b) | `6502a615357ea13ef9d2952321794216f86b268b` | 1 | unknown; unknown |
| [harshshekharhv/langflow-runtime](https://github.com/harshshekharhv/langflow-runtime/tree/426edd889b976eba599df8d7c61864b5c9e67ecf) | `426edd889b976eba599df8d7c61864b5c9e67ecf` | 1 | unknown; unknown |
| [hatoun-alshoail/nl-sql-json-pdf-report-challenge](https://github.com/hatoun-alshoail/nl-sql-json-pdf-report-challenge/tree/82cd0f5e1e158e3b8c91f348976e627ac05a913c) | `82cd0f5e1e158e3b8c91f348976e627ac05a913c` | 1 | unknown; license-text-collected; review-required |
| [itsmariodias/automate-workflows-langflow-n8n](https://github.com/itsmariodias/automate-workflows-langflow-n8n/tree/5f5c9f64ce207cc0a76d582cb0547bfc149d6491) | `5f5c9f64ce207cc0a76d582cb0547bfc149d6491` | 1 | unknown; unknown |
| [jastr945/langflow-vault-prisma-airs-agent](https://github.com/jastr945/langflow-vault-prisma-airs-agent/tree/0a72db9a9fbee61492e29154d815cff41086ef12) | `0a72db9a9fbee61492e29154d815cff41086ef12` | 1 | unknown; unknown |
| [jimbender1976/rag_langflow_ollama_redis_milvus](https://github.com/jimbender1976/rag_langflow_ollama_redis_milvus/tree/50dc98af94ac8b94dea6ecfdf6aa0b3516f9dc2f) | `50dc98af94ac8b94dea6ecfdf6aa0b3516f9dc2f` | 1 | unknown; unknown |
| [kiriti-badam/langflow-streamlit-demo](https://github.com/kiriti-badam/langflow-streamlit-demo/tree/1bcd8010f4d22147f9b5ac20bc476aeffb7e3c01) | `1bcd8010f4d22147f9b5ac20bc476aeffb7e3c01` | 1 | unknown; unknown |
| [melienherrera/personal-assistant-langflow](https://github.com/melienherrera/personal-assistant-langflow/tree/bc8f7999138078e19e4d857ecf496fe6a22f8a38) | `bc8f7999138078e19e4d857ecf496fe6a22f8a38` | 1 | unknown; unknown |
| [michelderu/wikipedia-langflow-streamlit](https://github.com/michelderu/wikipedia-langflow-streamlit/tree/1a66a22039ac6515b29b638420bb91e8ff26d5d3) | `1a66a22039ac6515b29b638420bb91e8ff26d5d3` | 1 | unknown; unknown |
| [misbahsy/InsightExpress](https://github.com/misbahsy/InsightExpress/tree/f735c278e9c7e568fbd9c8b4550c534077147efd) | `f735c278e9c7e568fbd9c8b4550c534077147efd` | 1 | unknown; unknown |
| [mkmr2020/LangFlow-Vector-Rag-demo](https://github.com/mkmr2020/LangFlow-Vector-Rag-demo/tree/a2a31e6f099721228001090974ee779489c27a8a) | `a2a31e6f099721228001090974ee779489c27a8a` | 1 | unknown; unknown |
| [mmuchsin/serambi-ai](https://github.com/mmuchsin/serambi-ai/tree/86a95a4a4d3c4183bf2d2480b59441e90e59f0f4) | `86a95a4a4d3c4183bf2d2480b59441e90e59f0f4` | 1 | NOASSERTION; license-text-collected; review-required |
| [mrbreo/tiktok-ai-bot](https://github.com/mrbreo/tiktok-ai-bot/tree/3c4b5a665ad194cec9dfa2164fd9b52c9e494483) | `3c4b5a665ad194cec9dfa2164fd9b52c9e494483` | 1 | unknown; unknown |
| [mrudu10/RAG-based-ProductAnalyzer](https://github.com/mrudu10/RAG-based-ProductAnalyzer/tree/3f98ef8753018aa0c27bbb2c9498b4a1fc984dc2) | `3f98ef8753018aa0c27bbb2c9498b4a1fc984dc2` | 1 | unknown; unknown |
| [nancybhardwaj89/TestCaseCompass-AdvancedRAGAssistant](https://github.com/nancybhardwaj89/TestCaseCompass-AdvancedRAGAssistant/tree/68ceca661ad43ef22c6598cccf9f0a33d5c21ee3) | `68ceca661ad43ef22c6598cccf9f0a33d5c21ee3` | 1 | unknown; unknown |
| [permitio/permit-langflow](https://github.com/permitio/permit-langflow/tree/9603ca0af8c6f817bbd1411b9327c2b8650f7140) | `9603ca0af8c6f817bbd1411b9327c2b8650f7140` | 1 | Apache-2.0; license-text-collected; review-required |
| [phact/langflow-run](https://github.com/phact/langflow-run/tree/adf66ad83a08be5b1593b447c63d498b7527ce32) | `adf66ad83a08be5b1593b447c63d498b7527ce32` | 1 | unknown; unknown |
| [pragatidev/AIAgentsBootcamp](https://github.com/pragatidev/AIAgentsBootcamp/tree/eb1c87bd067c9ae5cb0c3b25c94a0dd1d37f8537) | `eb1c87bd067c9ae5cb0c3b25c94a0dd1d37f8537` | 1 | MIT; license-text-collected; review-required |
| [rafifmuzaky/LangFlow-Capstone-Project](https://github.com/rafifmuzaky/LangFlow-Capstone-Project/tree/3dbde8fbb89e3cee5f80d2132b9e9f372c42c820) | `3dbde8fbb89e3cee5f80d2132b9e9f372c42c820` | 1 | unknown; unknown |
| [raka6march/Sentiment-Analyze-Langflow](https://github.com/raka6march/Sentiment-Analyze-Langflow/tree/b2c3c9c6db14e9a3bcc5f45b20b419444795b046) | `b2c3c9c6db14e9a3bcc5f45b20b419444795b046` | 1 | unknown; unknown |
| [reachmesrividyap-GH/03-Langflow-multireasoning-agentsworkflow](https://github.com/reachmesrividyap-GH/03-Langflow-multireasoning-agentsworkflow/tree/8f4a1a03908de49963a8a4906ec9cd687b01d063) | `8f4a1a03908de49963a8a4906ec9cd687b01d063` | 1 | unknown; unknown |
| [riskanputri/langflow-sentiment-analysis](https://github.com/riskanputri/langflow-sentiment-analysis/tree/d3998c6597a1a05e2120394e583a3e17b247bc7d) | `d3998c6597a1a05e2120394e583a3e17b247bc7d` | 1 | unknown; unknown |
| [rizvand/scraper-langflow](https://github.com/rizvand/scraper-langflow/tree/048532ed02a1486dfff9c8b6068872d2a93a1008) | `048532ed02a1486dfff9c8b6068872d2a93a1008` | 1 | unknown; unknown |
| [rohanurrahmanontu/langflow-rag-agent](https://github.com/rohanurrahmanontu/langflow-rag-agent/tree/e4e92a3d78c4e3f9a0bc2cf515b82d72e4af5340) | `e4e92a3d78c4e3f9a0bc2cf515b82d72e4af5340` | 1 | unknown; unknown |
| [sakshimagadum2/smartstudy-ai](https://github.com/sakshimagadum2/smartstudy-ai/tree/c64e3f2ebe5787778d585b714640856dac937d37) | `c64e3f2ebe5787778d585b714640856dac937d37` | 1 | unknown; unknown |
| [semanurcetinn/QA-with-Langflow-Rag-Structure](https://github.com/semanurcetinn/QA-with-Langflow-Rag-Structure/tree/29f5122cbb7f55c782dc23f83db0c6990ad09fe3) | `29f5122cbb7f55c782dc23f83db0c6990ad09fe3` | 1 | unknown; unknown |
| [shubhbansal44/Social-Media-Insights-AI-Agent](https://github.com/shubhbansal44/Social-Media-Insights-AI-Agent/tree/74b0ebff1879877632e973cb53d1efcc18cd3426) | `74b0ebff1879877632e973cb53d1efcc18cd3426` | 1 | MIT; license-text-collected; review-required |
| [siddharthlanke/rag-pipeline-using-langflow](https://github.com/siddharthlanke/rag-pipeline-using-langflow/tree/4cfed28015041aad52edcff976c11d10d1552c1a) | `4cfed28015041aad52edcff976c11d10d1552c1a` | 1 | MIT; license-text-collected; review-required |
| [slowlekar-iith/AgenticAI_Langflow](https://github.com/slowlekar-iith/AgenticAI_Langflow/tree/d4d887e35bdab368990807129510097784181995) | `d4d887e35bdab368990807129510097784181995` | 1 | Apache-2.0; license-text-collected; review-required |
| [srinikhil9/Langflow-Builder](https://github.com/srinikhil9/Langflow-Builder/tree/5dde4a9de1172c1acd026cdbca0e23a7a02faeaf) | `5dde4a9de1172c1acd026cdbca0e23a7a02faeaf` | 1 | MIT; license-text-collected; review-required |
| [techwithtim/Langflow-RAG-Tutorial](https://github.com/techwithtim/Langflow-RAG-Tutorial/tree/027f7e43b130748e99049e0b8192d60f739076c9) | `027f7e43b130748e99049e0b8192d60f739076c9` | 1 | unknown; unknown |
| [tehmenghai/rag-langflow](https://github.com/tehmenghai/rag-langflow/tree/ffa50f9f4227f0350b43a8675e447dc42dd23961) | `ffa50f9f4227f0350b43a8675e447dc42dd23961` | 1 | unknown; unknown |
| [tpires1041/DoaBot](https://github.com/tpires1041/DoaBot/tree/383f9e4c2054467ed9945d5355acb83c649e5e41) | `383f9e4c2054467ed9945d5355acb83c649e5e41` | 1 | GPL-3.0; license-text-collected; review-required |
| [trustassistAI/LangFlowRAGPipeline](https://github.com/trustassistAI/LangFlowRAGPipeline/tree/f7c6894744d08445c1584bed9f073e0b2b1e5ee5) | `f7c6894744d08445c1584bed9f073e0b2b1e5ee5` | 1 | unknown; unknown |
| [v5107005-del/digital-client-profile](https://github.com/v5107005-del/digital-client-profile/tree/ceee507c9f7ba8ce659b24cfec1975cad1d6eeeb) | `ceee507c9f7ba8ce659b24cfec1975cad1d6eeeb` | 1 | NOASSERTION; license-text-collected; review-required |
| [v5107005-del/prompt-engineering-examples](https://github.com/v5107005-del/prompt-engineering-examples/tree/0c96d0530fd24b3dff24b3cd5e5f6357b13909da) | `0c96d0530fd24b3dff24b3cd5e5f6357b13909da` | 1 | NOASSERTION; license-text-collected; review-required |
| [vanishreesjsu/genaidata_langflow](https://github.com/vanishreesjsu/genaidata_langflow/tree/4a02f6c67a22983ac12d96ce5ae45701d40944c9) | `4a02f6c67a22983ac12d96ce5ae45701d40944c9` | 1 | unknown; unknown |
| [victormdev/rag-agent-python-langflow](https://github.com/victormdev/rag-agent-python-langflow/tree/8ea5f1c0069549e84c0e38593103f1a47c05b275) | `8ea5f1c0069549e84c0e38593103f1a47c05b275` | 1 | unknown; unknown |
| [weber-stephen/founder-flow](https://github.com/weber-stephen/founder-flow/tree/703bc12bda7d0520a55dcc36d0dd245402bd2c3a) | `703bc12bda7d0520a55dcc36d0dd245402bd2c3a` | 1 | MIT; license-text-collected; review-required |
| [yashbhosale2403/ai-agents-lab](https://github.com/yashbhosale2403/ai-agents-lab/tree/eb58db8e11ca92073040a950fc721a1b285ea0c1) | `eb58db8e11ca92073040a950fc721a1b285ea0c1` | 1 | unknown; unknown |

The manifest preserves each original path, pinned raw source URL, repository, revision, SHA256, collection timestamp, byte length, license record, and fork flag. Failed candidates and download failures are retained in `failures`. Repositories with zero accepted graphs remain in `sources` as exclusions rather than being silently omitted.

## Final verification and follow-up sweep

All 2767 saved artifacts matched their recorded SHA256; mismatches: 0.

Schema evidence: langflow-export-metadata-or-node-template: 2662, generic-node-edge-graph-needs-review: 105. Generic node-edge graphs are retained as review candidates and must not automatically count as Langflow templates.

The follow-up sweep examined 18 paths, covering the initial 500-JSON limit in FelixFtch/SysML-AgentBench and retrying the one transient download timeout. All sweep downloads succeeded; the historical timeout remains in failures with its resolution in followupSweep. No eligible candidate paths remain unexamined in completed Git trees.

ACRT-EVAL repositories are explicitly labeled as derived evaluation repositories. Other repositories may also contain upstream starter templates or copied tutorial flows. The manifest sourceFamily field intentionally leaves such family attribution unresolved; exact byte duplication is measurable, semantic independence is not claimed.
