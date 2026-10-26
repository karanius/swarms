"""Opt-in search provider for V2; upstream Langflow components stay unchanged."""
from urllib.parse import parse_qs, urlparse

import json

import pandas as pd
import requests
from bs4 import BeautifulSoup

from lfx.components.data_source.web_search import WebSearchComponent
from lfx.schema import DataFrame, Message
from lfx.io import Output


class LiteWebSearchComponent(WebSearchComponent):
    display_name = "Web Search · Lite"
    description = "Search DuckDuckGo Lite using focused queries; return source URLs and snippets."
    name = "LiteWebSearch"
    outputs = [Output(name="results", display_name="Results", method="perform_search")]

    def perform_search(self) -> Message:
        if self.search_mode != "Web":
            raise ValueError("This provider supports Web mode only")
        rows = self.perform_web_search().to_dict(orient="records")
        return Message(text=json.dumps({"evidence_scope": "search_snippets_only", "results": rows}, ensure_ascii=False))

    def perform_web_search(self) -> DataFrame:
        query = self._sanitize_query(self.query)
        if not query:
            raise ValueError("Empty search query")
        response = requests.get(
            "https://lite.duckduckgo.com/lite/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        if response.status_code != 200 or soup.select_one("#challenge-form, #anomaly-form"):
            raise ValueError("Search provider returned a challenge; no verified results available")
        rows = []
        limit = self._get_limit("max_results", 5)
        for anchor in soup.select("a.result-link"):
            href = anchor.get("href", "")
            # parse_qs already decodes the redirect target exactly once.
            link = parse_qs(urlparse(href).query).get("uddg", [href])[0]
            if urlparse(link).scheme not in ("http", "https"):
                continue
            row = anchor.find_parent("tr")
            next_row = row.find_next_sibling("tr") if row else None
            snippet = next_row.select_one(".result-snippet") if next_row else None
            rows.append({"title": anchor.get_text(" ", strip=True), "link": link,
                         "snippet": snippet.get_text(" ", strip=True) if snippet else "",
                         "content": "", "source_type": "search_snippet"})
            if limit and len(rows) >= limit:
                break
        if not rows:
            raise ValueError("Search returned no usable source URLs; do not treat this as successful research")
        self.status = f"Retrieved {len(rows)} live search results (snippets only)"
        return DataFrame(pd.DataFrame(rows))
