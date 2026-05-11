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
    _init_.py
    crawler.py
    indexer.py
    search.py
    main.py
  tests/
    test_crawler.py
    test_indexer.py
    test_main.py
    test_search.py
  data/
    README.md
    index.json
  .gitgnore
  README.md
  pytest.ini
  requirements.txt
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

### How GenAI Was Used

| Area | Use | Details |
|------|-----|---------|
| **Crawler** | Boilerplate & error handling | Copilot suggested the structure of `fetch_page()` with `try/except` and `raise_for_status()`. It also proposed extracting visible text with `soup.get_text()`. |
| **Indexer** | Data structure ideas & JSON serialisation | AI helped generate the nested `setdefault` pattern for building the inverted index. It also suggested `sort_keys=True` and `indent=2` for reproducible JSON output. |
| **Search** | Set intersection logic | Copilot completed the `set.intersection(*page_sets)` line after I wrote the comment `# AND query`. |
| **Tests** | Test scaffolding | I used Copilot to generate initial test skeletons, then manually added edge cases (e.g., empty queries, non‑HTML responses, missing files). |
| **README & Documentation** | Drafting | AI assisted with rephrasing instructions and generating the project structure tree. I reviewed and adjusted everything for accuracy. |

#### Where GenAI Helped
- **Tokenisation regex**: Copilot suggested `r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?"` which correctly captures contractions like “don’t”. This saved me from manually researching possessive‑friendly regex patterns.
- **JSON serialisation parameters**: The AI recommended `ensure_ascii=True, indent=2, sort_keys=True`. This made the index file deterministic and easy to inspect – a detail I might have overlooked without the hint.
- **CLI loop structure**: Copilot generated a reliable `while True: cmd = input(...)` loop with command‑dispatching, which I then extended with custom error messages.

#### Where GenAI Hindered (or Required Significant Correction)
- **Misguided crawling logic**: When I asked Copilot to “get all internal links”, it initially produced code that extracted every `<a href>` and blindly followed them, which on a different site could lead to infinite crawling. I discarded that approach and instead implemented explicit scope control (`should_follow_link`) with a BFS queue – the correct solution for this assignment’s linear pagination.
- **Default‑dict over‑complication**: AI suggested using `defaultdict(lambda: defaultdict(dict))` for the index. While functional, it made the code harder to read and obfuscated the exact structure. I replaced it with explicit `.setdefault()` calls, which made the data model more transparent and easier to debug.
- **Test generation for edge cases**: AI‑generated tests covered the “happy paths” well, but completely missed critical scenarios like requesting a word before loading an index, or handling HTTP timeout exceptions. I manually added tests for these; they now form about 40% of my test suite.
- **Over‑optimisation temptation**: At one point Copilot suggested using a `lru_cache` for URL normalisation. This was unnecessary for a small static website and would have added complexity without any real benefit. I chose to keep the code straightforward.

### Reflection on Learning
- **Deepened understanding**: I deliberately wrote the inverted‑index construction loop and the scoring logic without AI assistance. Manually implementing `word_map.setdefault(word, {}).setdefault(url, {...})` forced me to internalise the nested dictionary structure and how search engines store postings lists. This hands‑on work was essential for my learning.
- **Debugging skills improved**: When AI‑generated code failed (e.g., the all‑links crawler), I had to trace the logic, identify the flaw, and redesign the approach. This strengthened my ability to reason about concurrent HTTP requests and crawl frontiers.
- **Critical evaluation habit**: Comparing my own solutions with AI proposals taught me to ask “why would this be better?” rather than accepting suggestions automatically. This critical mindset is a transferable skill I will carry into future projects.
- **Time management**: AI saved roughly 1‑2 hours on regex writing, CLI scaffolding, and JSON formatting details. However, debugging the misguided crawler logic and adding missing edge‑case tests took extra time (≈1 hour) that balanced out the gains. The net productivity effect was slightly positive, but the real value was in the learning process, not in raw speed.
- **Ethical consideration**: By using AI, I remained responsible for all submitted code. I ensured I could explain every line and justify every design choice during the video demonstration, in line with the University’s academic integrity guidelines.

### Declaration
I confirm that all GenAI usage in this project has been declared above. No undisclosed AI tools were used, and I fully understand every part of the codebase, regardless of its origin.

## References

- Requests documentation: https://requests.readthedocs.io/
- Beautiful Soup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Target website: https://quotes.toscrape.com/
