from pathlib import Path

from src.crawler import CrawledPage
from src.indexer import build_index, load_index, save_index, tokenize


def test_tokenize_is_case_insensitive_and_ignores_punctuation():
    assert tokenize("Good friends, GOOD books!") == [
        "good",
        "friends",
        "good",
        "books",
    ]


def test_build_index_records_frequency_and_positions():
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/page/1/",
            title="Page 1",
            text="Good friends and good books.",
            links=(),
        )
    ]

    index = build_index(pages)
    posting = index["index"]["good"]["https://quotes.toscrape.com/page/1/"]

    assert posting["frequency"] == 2
    assert posting["positions"] == [0, 3]
    assert index["metadata"]["page_count"] == 1
    assert index["pages"]["https://quotes.toscrape.com/page/1/"]["word_count"] == 5


def test_save_and_load_index_round_trip():
    index = build_index(
        [
            CrawledPage(
                url="https://quotes.toscrape.com/",
                title="Quotes",
                text="Simple quote",
                links=(),
            )
        ]
    )
    index_path = Path("data/test_index_round_trip.json")

    try:
        save_index(index, index_path)
        loaded = load_index(index_path)
    finally:
        index_path.unlink(missing_ok=True)

    assert loaded["index"]["simple"]["https://quotes.toscrape.com/"]["frequency"] == 1
