# Search Engine Tool

Coursework 2 project for COMP/XJCO3011 Web Services and Web Data.

## Project Overview

This project will implement a small command-line search engine for:

https://quotes.toscrape.com/

The tool will crawl the website, build an inverted index, save and load that index from disk, and allow users to search for pages containing specific query terms.

## Coursework Requirements Checklist

- [x] Crawl pages from `https://quotes.toscrape.com/`
- [x] Respect a politeness window of at least 6 seconds between website requests
- [x] Build a case-insensitive inverted index
- [x] Store word statistics such as frequency and/or position per page
- [x] Save the index to the file system
- [x] Load a previously saved index
- [x] Support the `build` command
- [x] Support the `load` command
- [x] Support the `print <word>` command
- [x] Support the `find <query terms>` command
- [x] Handle edge cases such as missing words, empty queries, and network errors
- [x] Include unit tests and clear testing instructions
- [ ] Maintain regular Git commits
- [ ] Prepare a 5-minute video demonstration
- [ ] Declare and critically evaluate any GenAI usage

## Repository Structure

```text
search-engine-tool/
  src/
    crawler.py
    indexer.py
    search.py
    main.py
  tests/
    test_crawler.py
    test_indexer.py
    test_search.py
  data/
    README.md
  requirements.txt
  README.md
```

## Installation

Install dependencies from the project root:

```bash
pip install -r requirements.txt
```

## Usage

The program supports both direct command mode and interactive shell mode.

Build the index:

```bash
python -m src.main build
```

This crawls `https://quotes.toscrape.com/`, waits at least 6 seconds between website requests, builds the inverted index, and saves it to `data/index.json`.

Load the saved index:

```bash
python -m src.main load
```

Print the inverted index for one word:

```bash
python -m src.main print nonsense
```

Find pages containing one or more query terms:

```bash
python -m src.main find good friends
```

Start the interactive shell:

```bash
python -m src.main
```

Then type commands in this style:

```text
> build
> load
> print nonsense
> find good friends
> exit
```

Useful development options:

```bash
python -m src.main --max-pages 2 --politeness-delay 0 build
```

This is only for quick local testing. Use the default 6-second politeness delay for the real coursework crawl.

## Testing

Run the test suite:

```bash
python -m pytest tests
```

Optional coverage command:

```bash
python -m pytest tests --cov=src
```

In this Windows environment, if pytest has permission problems with cache or temp directories, use:

```bash
python -m pytest tests -p no:cacheprovider
python -m pytest tests --cov=src -p no:cacheprovider
```

## Design Notes

The project is split into four main modules:

- `crawler.py`: performs a breadth-first crawl from the target website, keeps only internal links, extracts visible page text, and enforces the politeness window before repeated requests.
- `indexer.py`: tokenises text case-insensitively and builds a JSON-serialisable inverted index.
- `search.py`: implements single-word posting lookup and multi-word AND search.
- `main.py`: provides direct command mode and an interactive command-line shell.

The inverted index is stored as JSON with this shape:

```json
{
  "metadata": {
    "target": "https://quotes.toscrape.com/",
    "created_at": "...",
    "page_count": 1,
    "unique_words": 10
  },
  "pages": {
    "https://quotes.toscrape.com/": {
      "title": "Quotes to Scrape",
      "word_count": 100
    }
  },
  "index": {
    "good": {
      "https://quotes.toscrape.com/": {
        "frequency": 2,
        "positions": [4, 20]
      }
    }
  }
}
```

Multi-word searches require all query terms to appear on the returned page. Results are ranked by the total frequency of the matched query terms.

## GenAI Declaration

TODO: Add a clear declaration before submission.

Include:

- Which GenAI tools were used
- What they were used for
- Specific examples of where they helped
- Specific examples of where they caused issues or needed correction
- How GenAI affected learning, debugging, and time management

## References

- Requests documentation: https://requests.readthedocs.io/
- Beautiful Soup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Target website: https://quotes.toscrape.com/
