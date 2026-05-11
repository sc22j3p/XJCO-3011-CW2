from pathlib import Path
from src.crawler import CrawledPage
from src.indexer import build_index, save_index
from src.main import SearchEngineCLI


def make_cli_index(path):
    index = build_index(
        [
            CrawledPage(
                url="https://quotes.toscrape.com/page/1/",
                title="Page 1",
                text="Good friends are good company.",
                links=(),
            )
        ]
    )
    save_index(index, path)


def test_cli_load_print_and_find(capsys):
    index_path = Path("data/test_cli_index.json")
    make_cli_index(index_path)
    cli = SearchEngineCLI(index_path=index_path, politeness_delay=0)

    try:
        assert cli.handle(["load"]) is True
        assert cli.handle(["print", "good"]) is True
        assert cli.handle(["find", "good", "friends"]) is True
    finally:
        index_path.unlink(missing_ok=True)

    output = capsys.readouterr().out
    assert "Loaded index" in output
    assert "frequency" in output
    assert "https://quotes.toscrape.com/page/1/" in output


def test_cli_handles_missing_word_and_empty_query(capsys):
    index_path = Path("data/test_cli_missing_index.json")
    make_cli_index(index_path)
    cli = SearchEngineCLI(index_path=index_path, politeness_delay=0)

    try:
        cli.handle(["print", "missing"])
        cli.handle(["find"])
    finally:
        index_path.unlink(missing_ok=True)

    output = capsys.readouterr().out
    assert "No entries found" in output
    assert "Usage: find <query terms>" in output


def test_cli_exit_returns_false():
    cli = SearchEngineCLI(politeness_delay=0)

    assert cli.handle(["exit"]) is False


def test_cli_build_uses_crawler_and_saves_index(monkeypatch, capsys):
    index_path = Path("data/test_cli_build_index.json")

    class FakeCrawler:
        def __init__(self, base_url, politeness_delay, crawl_scope="quotes"):
            self.base_url = base_url
            self.politeness_delay = politeness_delay
            self.crawl_scope = crawl_scope

        def crawl(self, max_pages=None, show_progress=False):
            return [
                CrawledPage(
                    url="https://quotes.toscrape.com/",
                    title="Quotes",
                    text="Simple quote",
                    links=(),
                )
            ]

    monkeypatch.setattr("src.main.WebsiteCrawler", FakeCrawler)
    cli = SearchEngineCLI(index_path=index_path, politeness_delay=0, max_pages=1)

    try:
        cli.handle(["build"])
        assert index_path.exists()
    finally:
        index_path.unlink(missing_ok=True)

    output = capsys.readouterr().out
    assert "Built index" in output
    assert "Saved index" in output
