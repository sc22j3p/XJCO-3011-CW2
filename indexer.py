"""Build, save, and load an inverted index."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

if __package__:
    from .crawler import CrawledPage, TARGET_WEBSITE
else:  # pragma: no cover - supports direct script execution
    from crawler import CrawledPage, TARGET_WEBSITE


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_PATH = PROJECT_ROOT / "data" / "index.json"
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")

InvertedIndex = dict[str, Any]


def tokenize(text: str) -> list[str]:
    """Split text into case-insensitive searchable words."""

    return [match.group(0).lower() for match in WORD_PATTERN.finditer(text)]


def build_index(pages: Iterable[CrawledPage], target: str = TARGET_WEBSITE) -> InvertedIndex:
    """Create an inverted index from crawled pages.

    Index format:
    {
      "metadata": {...},
      "pages": {
        "url": {"title": "...", "word_count": 123}
      },
      "index": {
        "word": {
          "url": {"frequency": 2, "positions": [0, 8]}
        }
      }
    }
    """

    page_map: dict[str, dict[str, Any]] = {}
    word_map: dict[str, dict[str, dict[str, Any]]] = {}

    page_count = 0
    for page in pages:
        page_count += 1
        words = tokenize(page.text)
        page_map[page.url] = {
            "title": page.title,
            "word_count": len(words),
        }

        for position, word in enumerate(words):
            posting = word_map.setdefault(word, {}).setdefault(
                page.url,
                {"frequency": 0, "positions": []},
            )
            posting["frequency"] += 1
            posting["positions"].append(position)

    return {
        "metadata": {
            "target": target,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "page_count": page_count,
            "unique_words": len(word_map),
        },
        "pages": page_map,
        "index": word_map,
    }


def save_index(index: Mapping[str, Any], path: str | Path = DEFAULT_INDEX_PATH) -> Path:
    """Save an index to JSON and return the written path."""

    index_path = Path(path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(index, ensure_ascii=True, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return index_path


def load_index(path: str | Path = DEFAULT_INDEX_PATH) -> InvertedIndex:
    """Load a previously saved index from JSON."""

    index_path = Path(path)
    if not index_path.exists():
        raise FileNotFoundError(
            f"Index file not found: {index_path}. Run the build command first."
        )

    return json.loads(index_path.read_text(encoding="utf-8"))


def describe_index(index: Mapping[str, Any]) -> str:
    """Return a short human-readable summary of an index."""

    metadata = index.get("metadata", {})
    page_count = metadata.get("page_count", len(index.get("pages", {})))
    unique_words = metadata.get("unique_words", len(index.get("index", {})))
    return f"{page_count} pages, {unique_words} unique words"
