import pytest
from src.crawler import CrawledPage
from src.indexer import build_index
from src.search import find_pages, get_postings


@pytest.fixture
def sample_index():
    return build_index(
        [
            CrawledPage(
                url="https://quotes.toscrape.com/page/1/",
                title="Page 1",
                text="Good friends are good company.",
                links=(),
            ),
            CrawledPage(
                url="https://quotes.toscrape.com/page/2/",
                title="Page 2",
                text="Good books and quiet rooms.",
                links=(),
            ),
        ]
    )


def test_get_postings_returns_word_entry(sample_index):
    postings = get_postings(sample_index, "GOOD")

    assert set(postings) == {
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
    }


def test_find_pages_requires_all_terms_and_ranks_results(sample_index):
    results = find_pages(sample_index, "good friends")

    assert len(results) == 1
    assert results[0].url == "https://quotes.toscrape.com/page/1/"
    assert results[0].score == 3


def test_find_pages_returns_empty_list_for_missing_terms(sample_index):
    assert find_pages(sample_index, "missing term") == []


def test_find_pages_rejects_empty_query(sample_index):
    with pytest.raises(ValueError):
        find_pages(sample_index, "")
