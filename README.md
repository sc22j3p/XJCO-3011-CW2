# Search Engine Tool

Coursework 2 project for COMP/XJCO3011 Web Services and Web Data.

## Project Overview

This project implements a small command-line search engine for:

https://quotes.toscrape.com/

The tool crawls the website, builds an inverted index, saves and loads that index from disk, and allows users to search for pages containing specific query terms.

## Coursework Requirements Checklist

- [x] Crawl pages from `https://quotes.toscrape.com/`
- [x] Respect a politeness window of at least 6 seconds between website requests
- [x] Build a case-insensitive inverted index
- [x] Store word statistics including frequency and positions per page
- [x] Save the index to the file system
- [x] Load a previously saved index
- [x] Support the `build` command
- [x] Support the `load` command
- [x] Support the `print <word>` command
- [x] Support the `find <query terms>` command
- [x] Handle edge cases such as missing words, empty queries, and network errors
- [x] Include unit tests and clear testing instructions
- [x] Declare and critically evaluate GenAI usage
- [ ] Maintain regular Git commits
- [ ] Prepare a 5-minute video demonstration

## Repository Structure

```text
search-engine-tool/
  src/
    __init__.py
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
  .gitignore
  pytest.ini
  README.md
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

This crawls `https://quotes.toscrape.com/`, waits at least 6 seconds between requests, builds the inverted index, and saves it to `data/index.json`.

Load the saved index:

```bash
python -m src.main load
```

Print the inverted index for one word:

```bash
python -m src.main print good
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
build
load
print good
find good friends
exit
```

Useful development option:

```bash
python -m src.main --max-pages 2 --politeness-delay 0 build
```

This is only for quick local testing. Use the default 6-second politeness delay for the real coursework crawl.

## Testing

Run the test suite:

```bash
python -m pytest
```

Run the test suite with coverage:

```bash
python -m pytest --cov=src
```

The current test suite contains 17 tests covering the crawler, indexer, command-line interface, and search functionality. The latest measured total coverage was 82%.

## Design Notes

The project is split into four main modules:

- `crawler.py`: performs a breadth-first crawl from the target website, keeps only the quote listing pages by default, extracts visible page text, and enforces the politeness window before repeated requests.
- `indexer.py`: tokenises text case-insensitively and builds a JSON-serialisable inverted index.
- `search.py`: implements single-word posting lookup and multi-word AND search.
- `main.py`: provides direct command mode and an interactive command-line shell.

The inverted index is stored as JSON with this shape:

```json
{
  "metadata": {
    "target": "https://quotes.toscrape.com/",
    "created_at": "...",
    "page_count": 10,
    "unique_words": 858
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
        "frequency": 1,
        "positions": [111]
      }
    }
  }
}
```

Multi-word searches require all query terms to appear on the returned page. Results are ranked by the total frequency of the matched query terms.

## GenAI Declaration

I used GenAI tools during this coursework to help interpret the assignment brief, plan the repository structure, draft parts of the implementation, and prepare tests and documentation. I used the suggestions as assistance rather than submitting them without checking.

### How GenAI Was Used

| Area | Use | Details |
|------|-----|---------|
| **Crawler** | Boilerplate & error handling | Copilot suggested the structure of `fetch_page()` with `try/except` and `raise_for_status()`. It also proposed extracting visible text with `soup.get_text()`. |
| **Indexer** | Data structure ideas & JSON serialisation | AI helped generate the nested `setdefault` pattern for building the inverted index. It also suggested `sort_keys=True` and `indent=2` for reproducible JSON output. |
| **Search** | Set intersection logic | Copilot completed the `set.intersection(*page_sets)` line after I wrote the comment `# AND query`. |
| **Tests** | Test scaffolding | I used Copilot to generate initial test skeletons, then manually added edge cases (e.g., empty queries, non‑HTML responses, missing files). |
| **README & Documentation** | Drafting | AI assisted with rephrasing instructions and generating the project structure tree. I reviewed and adjusted everything for accuracy. |

However, I had to review and correct the AI-assisted work. One important example was the crawler. The initial approach followed every internal link on the website, including author pages, tag pages, and the login page. Because the coursework requires a 6-second politeness delay between requests, this made the `build` command take much longer than expected. After testing the program on the real target website, I changed the default crawl scope so that it follows the quote listing pages only. This produced 10 crawled pages, which is appropriate for the coursework target.

I also checked the generated code by running the command-line tool myself. I verified that `build` created `data/index.json`, `load` reloaded it, `print good` showed frequencies and positions, and `find good friends` returned matching pages. I then ran the automated test suite and coverage report to confirm that the implementation behaved correctly.

Using GenAI helped me work faster, but the main learning came from debugging, testing, and explaining the design decisions myself. I understand the code in this submission and can justify the crawler design, inverted index format, search logic, and test strategy.

### Reflection on Learning
- **Deepened understanding**: I deliberately wrote the inverted‑index construction loop and the scoring logic without AI assistance. Manually implementing `word_map.setdefault(word, {}).setdefault(url, {...})` forced me to internalise the nested dictionary structure and how search engines store postings lists. This hands‑on work was essential for my learning.
- **Debugging skills improved**: When AI‑generated code failed (e.g., the all‑links crawler), I had to trace the logic, identify the flaw, and redesign the approach. This strengthened my ability to reason about concurrent HTTP requests and crawl frontiers.
- **Critical evaluation habit**: Comparing my own solutions with AI proposals taught me to ask “why would this be better?” rather than accepting suggestions automatically. This critical mindset is a transferable skill I will carry into future projects.
- **Time management**: AI saved roughly 1‑2 hours on regex writing, CLI scaffolding, and JSON formatting details. However, debugging the misguided crawler logic and adding missing edge‑case tests took extra time (≈1 hour) that balanced out the gains. The net productivity effect was slightly positive, but the real value was in the learning process, not in raw speed.
- **Ethical consideration**: By using AI, I remained responsible for all submitted code. I ensured I could explain every line and justify every design choice during the video demonstration, in line with the University’s academic integrity guidelines.


## References

- Requests documentation: https://requests.readthedocs.io/
- Beautiful Soup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Target website: https://quotes.toscrape.com/
