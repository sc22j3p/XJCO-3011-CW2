"""Query operations for the inverted index."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

if __package__:
    from .indexer import tokenize
else:  # pragma: no cover - supports direct script execution
    from indexer import tokenize


@dataclass(frozen=True)
class SearchResult:
    """One matching page returned by a query."""

    url: str
    title: str
    score: int
    matched_terms: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
        }


def get_postings(index: Mapping[str, Any], word: str) -> dict[str, Any]:
    """Return the inverted-index entry for one word."""

    terms = tokenize(word)
    if len(terms) != 1:
        raise ValueError("print expects exactly one searchable word")
    return dict(index.get("index", {}).get(terms[0], {}))


def find_pages(index: Mapping[str, Any], query: str | Sequence[str]) -> list[SearchResult]:
    """Find pages containing all query terms, ranked by total frequency."""

    if isinstance(query, str):
        terms = tokenize(query)
    else:
        terms = tokenize(" ".join(query))

    unique_terms = tuple(dict.fromkeys(terms))
    if not unique_terms:
        raise ValueError("find expects at least one searchable word")

    index_body = index.get("index", {})
    page_sets = [set(index_body.get(term, {}).keys()) for term in unique_terms]
    if not page_sets or any(not pages for pages in page_sets):
        return []

    matching_urls = set.intersection(*page_sets)
    pages = index.get("pages", {})
    results: list[SearchResult] = []

    for url in matching_urls:
        score = sum(index_body[term][url]["frequency"] for term in unique_terms)
        page_data = pages.get(url, {})
        results.append(
            SearchResult(
                url=url,
                title=page_data.get("title", ""),
                score=score,
                matched_terms=unique_terms,
            )
        )

    return sorted(results, key=lambda result: (-result.score, result.url))
