import pytest

from src.crawler import CrawlError, WebsiteCrawler


class FakeResponse:
    def __init__(
        self,
        text,
        url="https://quotes.toscrape.com/",
        status_code=200,
        content_type="text/html",
    ):
        self.text = text
        self.url = url
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"{self.status_code} error")


class FakeSession:
    def __init__(self, pages):
        self.pages = pages
        self.requested_urls = []

    def get(self, url, timeout):
        self.requested_urls.append(url)
        response = self.pages[url]
        if isinstance(response, Exception):
            raise response
        return response


def test_normalise_url_removes_fragment_and_lowercases_host():
    url = WebsiteCrawler.normalise_url("HTTPS://Quotes.ToScrape.Com/page/1/#quote")

    assert url == "https://quotes.toscrape.com/page/1/"


def test_extract_internal_links_keeps_only_target_site():
    crawler = WebsiteCrawler(politeness_delay=0)
    html = """
    <html>
      <body>
        <a href="/page/2/">Next</a>
        <a href="https://quotes.toscrape.com/author/Albert-Einstein/">Author</a>
        <a href="https://example.com/outside">Outside</a>
      </body>
    </html>
    """
    from bs4 import BeautifulSoup

    parsed = BeautifulSoup(html, "html.parser")
    links = crawler.extract_internal_links(parsed, "https://quotes.toscrape.com/")

    assert links == [
        "https://quotes.toscrape.com/author/Albert-Einstein/",
        "https://quotes.toscrape.com/page/2/",
    ]


def test_extract_visible_text_ignores_script_and_style():
    from bs4 import BeautifulSoup

    parsed = BeautifulSoup(
        "<html><style>.x{}</style><script>alert(1)</script><p>Hello world</p></html>",
        "html.parser",
    )

    assert WebsiteCrawler.extract_visible_text(parsed) == "Hello world"


def test_fetch_page_extracts_title_text_and_links():
    html = """
    <html>
      <head><title>Quotes</title></head>
      <body>
        <p>Good quote</p>
        <a href="/page/2/">Next</a>
      </body>
    </html>
    """
    session = FakeSession(
        {"https://quotes.toscrape.com/": FakeResponse(html)}
    )
    crawler = WebsiteCrawler(politeness_delay=0, session=session)

    page = crawler.fetch_page("https://quotes.toscrape.com/")

    assert page.title == "Quotes"
    assert "Good quote" in page.text
    assert page.links == ("https://quotes.toscrape.com/page/2/",)


def test_fetch_page_rejects_non_html_content():
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": FakeResponse(
                "not html",
                content_type="application/pdf",
            )
        }
    )
    crawler = WebsiteCrawler(politeness_delay=0, session=session)

    with pytest.raises(CrawlError):
        crawler.fetch_page("https://quotes.toscrape.com/")


def test_crawl_follows_internal_links_once():
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": FakeResponse(
                '<a href="/page/2/">Next</a><p>Home</p>',
                url="https://quotes.toscrape.com/",
            ),
            "https://quotes.toscrape.com/page/2/": FakeResponse(
                '<a href="/">Home</a><p>Second page</p>',
                url="https://quotes.toscrape.com/page/2/",
            ),
        }
    )
    crawler = WebsiteCrawler(politeness_delay=0, session=session)

    pages = crawler.crawl()

    assert [page.url for page in pages] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert session.requested_urls == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
