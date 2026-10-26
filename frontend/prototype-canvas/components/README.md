# V2 opt-in search provider

`lite_web_search.py` defines **Web Search · Lite**, a custom subclass of Langflow's existing Web Search. The upstream implementation is unchanged. The dedicated V2 Deep Research graph stores this source in its normal component code field, retaining native rendering, tool wiring, and backend execution.

The original DuckDuckGo HTML endpoint returned HTTP 403 on this machine. The Lite endpoint returned actual search results for focused study queries. This provider uses that endpoint without the HTML endpoint's region parameter, decodes redirect targets once, and parses Lite's result rows. It returns titles, URLs, and snippets, explicitly labeled `search_snippet`, in a JSON Message so Langflow’s table formatter cannot hide evidence from the model; it does not retrieve full papers. HTTP errors, challenges, and pages without results fail explicitly. Public search availability is not guaranteed.

Use focused queries (about 4–8 keywords), one study per query. The researcher instructions in the configured graph state the evidence limit and require disclosure of failed requests. No search credentials, VPN changes, or alterations to original Langflow source are involved.

Tests, with the local Langflow Python environment:

```sh
/Users/x/projects/langflow/.venv/bin/python frontend/prototype-canvas/components/test_lite_web_search.py
```

These checks cover result extraction, exact-once URL decoding, HTTP 403, challenges, and empty responses. Live tests also returned three URLs with snippets for each of three remote-work study queries. A successful search does not independently establish factual correctness of the final report.
