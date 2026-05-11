"""Website crawler for the coursework search engine."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Iterable, Literal
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


TARGET_WEBSITE = "https://quotes.toscrape.com/"
DEFAULT_POLITENESS_DELAY = 6.0
DEFAULT_TIMEOUT = 15
CrawlScope = Literal["quotes", "all"]


@dataclass(frozen=True)
class CrawledPage:
    """Text and link data extracted from one crawled page."""

    url: str
    title: str
    text: str
    links: tuple[str, ...]


class CrawlError(RuntimeError):
    """Raised when a page cannot be fetched successfully."""


class WebsiteCrawler:
    """Crawl pages from one website while respecting a politeness delay."""

    def __init__(
        self,
        base_url: str = TARGET_WEBSITE,
        politeness_delay: float = DEFAULT_POLITENESS_DELAY,
        timeout: int = DEFAULT_TIMEOUT,
        crawl_scope: CrawlScope = "quotes",
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = self.normalise_url(base_url)
        self.politeness_delay = politeness_delay
        self.timeout = timeout
        self.crawl_scope = crawl_scope
        self.session = session or requests.Session()
        self._last_request_time: float | None = None
        self._base_parsed = urlparse(self.base_url)
        self._base_netloc = self._base_parsed.netloc

    @staticmethod
    def normalise_url(url: str) -> str:
        """Return a stable absolute URL without fragments."""

        clean_url, _fragment = urldefrag(url.strip())
        parsed = urlparse(clean_url)
        path = parsed.path or "/"
        return urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                path,
                "",
                parsed.query,
                "",
            )
        )

    def is_internal_url(self, url: str) -> bool:
        """Return True when the URL belongs to the configured website."""

        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.netloc == self._base_netloc

    def normalise_internal_url(self, url: str) -> str:
        """Normalise an internal URL and keep the configured scheme stable."""

        normalised = self.normalise_url(url)
        parsed = urlparse(normalised)
        if parsed.netloc == self._base_netloc:
            path = "/" if parsed.path.rstrip("/") == "/page/1" else parsed.path
            return urlunparse(
                (
                    self._base_parsed.scheme,
                    parsed.netloc,
                    path,
                    "",
                    parsed.query,
                    "",
                )
            )
        return normalised

    def should_follow_link(self, url: str) -> bool:
        """Decide whether the crawler should follow this internal link."""

        if self.crawl_scope == "all":
            return True

        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        return path == "" or (path.startswith("/page/") and path[6:].isdigit())

    def crawl(self, max_pages: int | None = None, show_progress: bool = False) -> list[CrawledPage]:
        """Breadth-first crawl of internal pages starting from the base URL."""

        queue = [self.base_url]
        queued = {self.base_url}
        visited: set[str] = set()
        pages: list[CrawledPage] = []

        while queue and (max_pages is None or len(pages) < max_pages):
            current_url = queue.pop(0)
            queued.discard(current_url)

            if current_url in visited:
                continue

            try:
                page = self.fetch_page(current_url)
            except CrawlError as exc:
                print(f"Warning: skipped {current_url}: {exc}")
                visited.add(current_url)
                continue

            pages.append(page)
            visited.add(current_url)
            if show_progress:
                print(f"Fetched {len(pages)} page(s): {page.url}", flush=True)

            for link in page.links:
                if self.should_follow_link(link) and link not in visited and link not in queued:
                    queue.append(link)
                    queued.add(link)

        return pages

    def fetch_page(self, url: str) -> CrawledPage:
        """Fetch one page and extract its visible text and internal links."""

        self._wait_if_needed()
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CrawlError(str(exc)) from exc

        content_type = response.headers.get("Content-Type", "")
        if content_type and "html" not in content_type.lower():
            raise CrawlError(f"unsupported content type: {content_type}")

        self._last_request_time = time.monotonic()
        soup = BeautifulSoup(response.text, "html.parser")

        return CrawledPage(
            url=self.normalise_internal_url(response.url or url),
            title=self.extract_title(soup),
            text=self.extract_visible_text(soup),
            links=tuple(self.extract_internal_links(soup, url)),
        )

    def _wait_if_needed(self) -> None:
        if self._last_request_time is None or self.politeness_delay <= 0:
            return

        elapsed = time.monotonic() - self._last_request_time
        remaining = self.politeness_delay - elapsed
        if remaining > 0:
            time.sleep(remaining)

    @staticmethod
    def extract_title(soup: BeautifulSoup) -> str:
        """Extract a readable page title."""

        if soup.title and soup.title.string:
            return soup.title.string.strip()
        first_heading = soup.find(["h1", "h2"])
        return first_heading.get_text(" ", strip=True) if first_heading else ""

    @staticmethod
    def extract_visible_text(soup: BeautifulSoup) -> str:
        """Extract visible page text while ignoring non-content elements."""

        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        return soup.get_text(" ", strip=True)

    def extract_internal_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Return normalised internal links found on the page."""

        links: set[str] = set()
        for tag in soup.find_all("a", href=True):
            absolute_url = self.normalise_internal_url(urljoin(current_url, tag["href"]))
            if self.is_internal_url(absolute_url):
                links.add(absolute_url)
        return sorted(links)


def crawl_website(
    base_url: str = TARGET_WEBSITE,
    politeness_delay: float = DEFAULT_POLITENESS_DELAY,
    max_pages: int | None = None,
    crawl_scope: CrawlScope = "quotes",
) -> list[CrawledPage]:
    """Convenience wrapper used by the command-line interface."""

    crawler = WebsiteCrawler(
        base_url=base_url,
        politeness_delay=politeness_delay,
        crawl_scope=crawl_scope,
    )
    return crawler.crawl(max_pages=max_pages, show_progress=True)
