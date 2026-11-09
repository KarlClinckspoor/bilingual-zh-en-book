# Data files

| File | Source | License |
|---|---|---|
| `hsk30-expanded.csv`, `hsk30-chars.csv` | HSK 3.0 word/character lists (2021 standard), github.com/ivankra/hsk30 | MIT, © 2023 Ivan Krasilnikov |
| `cedict_ts.u8.gz` | CC-CEDICT Chinese–English dictionary, published by MDBG (cc-cedict.org) | CC BY-SA 4.0 |

Refresh them with `python fetch_data.py`. HSK levels 7, 8 and 9 share one list in the official standard;
they are reported together as "7-9" (stored as level 7).

If a book uses CC-CEDICT glosses (words annotated without a gloss of their own), `make_book.py` prints
the CC-CEDICT attribution on the title page automatically, as the license requires.
