"""Command-line interface for the coursework search engine."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__:
    from .crawler import DEFAULT_POLITENESS_DELAY, TARGET_WEBSITE, CrawlScope, WebsiteCrawler
    from .indexer import DEFAULT_INDEX_PATH, build_index, describe_index, load_index, save_index
    from .search import find_pages, get_postings
else:  # pragma: no cover - supports direct script execution
    from crawler import DEFAULT_POLITENESS_DELAY, TARGET_WEBSITE, CrawlScope, WebsiteCrawler
    from indexer import DEFAULT_INDEX_PATH, build_index, describe_index, load_index, save_index
    from search import find_pages, get_postings


HELP_TEXT = """Commands:
  build [max_pages]      Crawl the website, build the index, and save it
  load                   Load the saved index from disk
  print <word>           Print the inverted index entry for one word
  find <query terms>     Find pages containing all query terms
  help                   Show this help text
  exit                   Leave interactive mode
"""


class SearchEngineCLI:
    """Stateful command handler used by both direct commands and the shell."""

    def __init__(
        self,
        index_path: str | Path = DEFAULT_INDEX_PATH,
        base_url: str = TARGET_WEBSITE,
        politeness_delay: float = DEFAULT_POLITENESS_DELAY,
        max_pages: int | None = None,
        crawl_scope: CrawlScope = "quotes",
    ) -> None:
        self.index_path = Path(index_path)
        self.base_url = base_url
        self.politeness_delay = politeness_delay
        self.max_pages = max_pages
        self.crawl_scope = crawl_scope
        self.index: dict[str, Any] | None = None

    def handle(self, parts: Sequence[str]) -> bool:
        """Run one command. Return False when the shell should exit."""

        if not parts:
            return True

        command = parts[0].lower()
        args = list(parts[1:])

        try:
            if command == "build":
                self.command_build(args)
            elif command == "load":
                self.command_load()
            elif command == "print":
                self.command_print(args)
            elif command == "find":
                self.command_find(args)
            elif command == "help":
                print(HELP_TEXT)
            elif command in {"exit", "quit"}:
                return False
            else:
                print(f"Unknown command: {command}. Type 'help' for commands.")
        except (FileNotFoundError, ValueError, OSError) as exc:
            print(f"Error: {exc}")

        return True

    def command_build(self, args: Sequence[str] = ()) -> None:
        max_pages = self.max_pages
        if args:
            if len(args) != 1 or not args[0].isdigit():
                raise ValueError("Usage: build [max_pages]")
            max_pages = int(args[0])

        print(f"Crawling {self.base_url}")
        print(f"Politeness delay: {self.politeness_delay:g} seconds")
        print(f"Crawl scope: {self.crawl_scope}")
        if max_pages is not None:
            print(f"Maximum pages: {max_pages}")

        crawler = WebsiteCrawler(
            base_url=self.base_url,
            politeness_delay=self.politeness_delay,
            crawl_scope=self.crawl_scope,
        )
        pages = crawler.crawl(max_pages=max_pages, show_progress=True)
        self.index = build_index(pages, target=self.base_url)
        output_path = save_index(self.index, self.index_path)

        print(f"Built index: {describe_index(self.index)}")
        print(f"Saved index to {output_path}")

    def command_load(self) -> None:
        self.index = load_index(self.index_path)
        print(f"Loaded index: {describe_index(self.index)}")

    def command_print(self, args: Sequence[str]) -> None:
        if len(args) != 1:
            raise ValueError("Usage: print <word>")
        index = self._require_index()
        postings = get_postings(index, args[0])
        if not postings:
            print(f"No entries found for '{args[0]}'.")
            return
        print(json.dumps(postings, ensure_ascii=False, indent=2, sort_keys=True))

    def command_find(self, args: Sequence[str]) -> None:
        if not args:
            raise ValueError("Usage: find <query terms>")
        index = self._require_index()
        results = find_pages(index, args)
        if not results:
            print("No matching pages found.")
            return
        for number, result in enumerate(results, start=1):
            title = f" ({result.title})" if result.title else ""
            print(f"{number}. {result.url}{title} [score={result.score}]")

    def _require_index(self) -> dict[str, Any]:
        if self.index is None:
            self.command_load()
        if self.index is None:
            raise ValueError("Index is not loaded.")
        return self.index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Coursework search engine command-line tool.",
    )
    parser.add_argument(
        "--index-path",
        default=str(DEFAULT_INDEX_PATH),
        help="Path to the JSON index file.",
    )
    parser.add_argument(
        "--base-url",
        default=TARGET_WEBSITE,
        help="Website to crawl.",
    )
    parser.add_argument(
        "--politeness-delay",
        type=float,
        default=DEFAULT_POLITENESS_DELAY,
        help="Seconds to wait between website requests.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional crawl limit for testing or debugging.",
    )
    parser.add_argument(
        "--crawl-scope",
        choices=["quotes", "all"],
        default="quotes",
        help="Use 'quotes' for quote listing pages only, or 'all' for every internal link.",
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="Optional command. Without a command, interactive shell mode starts.",
    )
    return parser


def run_shell(cli: SearchEngineCLI) -> None:
    print("Search Engine Tool interactive shell. Type 'help' for commands.")
    while True:
        try:
            raw_command = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            parts = shlex.split(raw_command)
        except ValueError as exc:
            print(f"Error: {exc}")
            continue

        if not cli.handle(parts):
            break


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cli = SearchEngineCLI(
        index_path=args.index_path,
        base_url=args.base_url,
        politeness_delay=args.politeness_delay,
        max_pages=args.max_pages,
        crawl_scope=args.crawl_scope,
    )

    if args.command:
        cli.handle(args.command)
    else:
        run_shell(cli)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
