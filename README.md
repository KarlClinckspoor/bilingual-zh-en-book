# zhbook – dual-language Chinese / English books

Graded Chinese reading texts for learners, laid out as facing-page Chinese / English booklets, plus
the free tool that builds them.

## Read the stories

Each PDF has Chinese on the left page and English on the right. Word boundaries are underlined, and
names, terms and words above the target level are footnoted with pinyin and meaning. Click a PDF to
read it in the browser, or download a whole level as one zip from the **Releases** page.

### HSK 3.0 level 4

| # | 中文 | English | theme | PDF |
|---|---|---|---|---|
| 01 | 中国茶 | Tea in China | culture & daily life | [PDF](stories/hsk4/01-tea/01-tea.pdf) |
| 02 | 中国各地的饮食 | Food Across China | culture & daily life | [PDF](stories/hsk4/02-regional-food/02-regional-food.pdf) |
| 03 | 汉字的故事 | How Chinese Characters Work | language | [PDF](stories/hsk4/03-chinese-characters/03-chinese-characters.pdf) |
| 04 | 城市里的一天 | A Day in a Chinese City | culture & daily life | [PDF](stories/hsk4/04-a-day-in-the-city/04-a-day-in-the-city.pdf) |
| 05 | 长城：传说与事实 | The Great Wall: Myth and Fact | history | [PDF](stories/hsk4/05-great-wall/05-great-wall.pdf) |
| 06 | 中国人的名字和称呼 | Chinese Names and Family Terms | language, culture & daily life | [PDF](stories/hsk4/06-names-and-family/06-names-and-family.pdf) |
| 07 | 二十四节气 | The 24 Solar Terms | nature & calendar | [PDF](stories/hsk4/07-solar-terms/07-solar-terms.pdf) |
| 08 | 3D打印是怎么工作的 | How 3D Printing Works | science & technology | [PDF](stories/hsk4/08-3d-printing/08-3d-printing.pdf) |
| 09 | 四大发明 | The Four Great Inventions | history, science & technology | [PDF](stories/hsk4/09-four-great-inventions/09-four-great-inventions.pdf) |
| 10 | 三国的故事 | The Three Kingdoms | history | [PDF](stories/hsk4/10-three-kingdoms/10-three-kingdoms.pdf) |
| 11 | 秦始皇 | Qin Shi Huang | history | [PDF](stories/hsk4/11-qin-shi-huang/11-qin-shi-huang.pdf) |

### HSK 3.0 level 5

Ten narrative short stories with dialogue, each practising four focus grammar points
(see [stories/hsk5](stories/hsk5/) for the grammar of each story).

| # | 中文 | English | theme | PDF |
|---|---|---|---|---|
| 12 | 胡同里的修表师傅 | The Watch Repairer of the Hutong | society, tradition & ideas | [PDF](stories/hsk5/12-watch-repairer/12-watch-repairer.pdf) |
| 13 | 郑和下西洋 | Zheng He Sails the Western Seas | history | [PDF](stories/hsk5/13-zheng-he/13-zheng-he.pdf) |
| 14 | 回村的女孩 | The Girl Who Went Back to the Village | society, culture & daily life | [PDF](stories/hsk5/14-back-to-the-village/14-back-to-the-village.pdf) |
| 15 | 塞翁失马 | Old Sai Loses His Horse | tradition & ideas, language | [PDF](stories/hsk5/15-sai-weng/15-sai-weng.pdf) |
| 16 | 变脸 | The Face-Changer's Apprentice | tradition & ideas | [PDF](stories/hsk5/16-face-changing/16-face-changing.pdf) |
| 17 | 高考那一年 | The Year of the Gaokao | society | [PDF](stories/hsk5/17-gaokao/17-gaokao.pdf) |
| 18 | 大熊猫回家 | Bringing the Pandas Home | nature & environment, science & technology | [PDF](stories/hsk5/18-pandas/18-pandas.pdf) |
| 19 | 沙漠里的驼铃 | Camel Bells in the Desert | history | [PDF](stories/hsk5/19-silk-road/19-silk-road.pdf) |
| 20 | 外婆的药箱 | Grandma's Medicine Chest | culture & daily life, science & technology | [PDF](stories/hsk5/20-medicine-chest/20-medicine-chest.pdf) |
| 21 | 月亮上的脚印 | Footprints on the Moon | science & technology, tradition & ideas | [PDF](stories/hsk5/21-moon/21-moon.pdf) |

The full catalogue of all levels is in [stories/README.md](stories/README.md).

**About the texts.** All texts and translations were written by Claude (Anthropic), an AI model.
They have been checked with the scripts in this repository but may still contain errors. Please open
an issue if you find one. Each story's source (`.zhb` / `.jsonl`) sits next to its PDF, so
corrections are easy to make.

## How the tool works

Lays out a Chinese text and its English translation as facing pages:

* **left (even) page:** Chinese on a fixed square grid. Every character and every punctuation mark
  takes exactly one cell, and nothing is compressed or stretched.
* **right (odd) page:** the English translation.
* **paragraph sync:** each paragraph starts on the same row of both pages and carries the same
  paragraph number in the outer margin. A paragraph too long for the spread is split at a sentence
  boundary, and both halves continue on the next spread.
* **reading aids (optional):**
  * every word is underlined, so learners can see word boundaries;
  * names get a double underline;
  * names, festival or technical terms, idioms and words above a chosen HSK 3.0 level get a mark
    (†, ‡, §… or numbers) with pinyin and meaning in a note at the foot of the page.

Free tools only: Python 3.9+ (standard library only) and XeLaTeX. Supports A5 (default) and A4.

```
existing text ──prepare.py──► batches/*.md ──Claude──► *.zhb ──zhb2jsonl.py──► book.jsonl
                                    (chat, or annotate_api.py)                     │
new text: ask Claude for .zhb directly ────────────────────────────────────────────┤
                                                       validate.py / hsk_report.py ┤
                                                                 make_book.py ─────┴──► book.pdf
```

## Requirements

* **Python 3.9 or newer.** No packages are needed, except `anthropic` for the optional `annotate_api.py`.
* **XeLaTeX** from TeX Live or MiKTeX, with `fontspec`, `fancyhdr` and `xcolor`, all standard.
* **Fonts.** The defaults are *Noto Serif CJK SC* (free, from Google Fonts / notofonts) and
  *TeX Gyre Pagella* (ships with TeX Live and MiKTeX).
  * On Windows, either install Noto Serif CJK SC or pass a font you already have, e.g.
    `--zh-font "SimSun" --zh-head-font "SimHei"` or `--zh-font "KaiTi"`.
  * The name must be what XeLaTeX sees. List the names with `fc-list :lang=zh family`.

## Quick start

```bash
python make_book.py examples/festivals/festivals.jsonl -o examples/festivals/build
```

The example is a short article on the Spring, Dragon Boat and Mid-Autumn festivals. It is written to
stay mostly at or below HSK 4: 91% of running words are at HSK 4 or below, and most of the rest are
festival terms. To see its level profile:

```bash
python hsk_report.py examples/festivals/festivals.jsonl --target 4
```

## Workflows

### A. A new text written by Claude

1. Ask Claude for a story or article in the `.zhb` format and paste `prompts/annotate.md` with the
   request. For example: "Write a 1500-character story about …, mostly HSK 4, in zhb format following
   these rules".
2. Save the answer as `mytext.zhb` and convert it:

   ```bash
   python zhb2jsonl.py mytext.zhb            # → mytext.jsonl
   python validate.py mytext.jsonl --annotate-above 4
   python hsk_report.py mytext.jsonl --target 4
   python make_book.py mytext.jsonl -o build/mytext
   ```

### B. An existing Chinese text, with or without a translation

```bash
python prepare.py original.txt --en translation.txt -o work/book --title-zh "…" --title-en "…"
```

* **Input files:** paragraphs are separated by blank lines. `# ` starts a chapter heading and `## `
  starts a section heading.
* **The translation is optional.** Without it, Claude translates. If you supply one, both files must
  have the same paragraph structure, and Claude only distributes the English over sentences without
  rewriting it.
* **Output:** `work/book/batches/batch_001.md …`, each about 1500 hanzi (`--batch-chars`).
* **Annotating the batches,** either way:
  * **By hand:** paste each `.md` into a Claude chat and save the reply's code block as `batch_001.zhb`
    and so on, next to the `.md`.
  * **Automatically:** `python annotate_api.py work/book` (needs `pip install anthropic` and
    `ANTHROPIC_API_KEY`, and is billed to your API account). It retries a batch once if the
    validator rejects it.

Then:

```bash
python zhb2jsonl.py work/book/batches/*.zhb -o work/book/book.jsonl
python validate.py work/book/book.jsonl --source work/book/source.jsonl
python make_book.py work/book/meta.jsonl work/book/book.jsonl -o work/book/build
```

**Why the validator matters.** Annotations come from a language model, so they can contain mistakes.
`validate.py --source` refuses any record whose tokens do not reproduce the original text character
for character. It also checks for:

* pinyin with the wrong number of syllables, an illegal syllable or a misplaced tone mark;
* pinyin that disagrees with CC-CEDICT. This is reported as WARN when it is a real disagreement and
  as INFO for neutral-tone differences only.

Fix the readings you disagree with directly in the `.zhb` or `.jsonl`. They then stay fixed, since
nothing is regenerated at build time.

## Formats

### `.zhb` (authoring / LLM output)

```
@meta {"title_zh": "中国的三个传统节日", "title_en": "Three Traditional Chinese Festivals"}
@h2 sec1
春节|Chūnjié|Spring_Festival|J
> The Spring Festival
@p p1
春节|Chūnjié 在|zài 农历|nónglì|lunar_calendar|J 正月|zhēngyuè|first_lunar_month|J 初一|chūyī ，
> It falls on the first day of the first lunar month.
```

* **Tokens.** A token is `word|pinyin|gloss|kind`. Punctuation is a bare token, and `_` stands for a
  space.
* **Segments.** A segment holds the tokens of one or more sentences and is closed by its `> English`
  line. Segments are the units used for alignment and page splitting.
* **Inheritance.** A token without gloss or kind inherits them from an earlier occurrence of the same
  word and pinyin.
* **Kinds:**
  * `N`: proper names. These get a double underline.
  * `J`: terms or cultural items.
  * `I`: idioms or set phrases.

  All three kinds are footnoted unless the word itself is in the HSK list at or below the
  `--annotate-above` level.

### `.jsonl` (canonical; one record per line)

```json
{"type":"meta","title_zh":"…","subtitle_zh":"…","title_en":"…","subtitle_en":"…","author":"…","note":"…"}
{"type":"h2","id":"sec1","zh":"春节","segs":[{"en":"The Spring Festival","tok":[["春节","Chūnjié","Spring Festival","J"]]}]}
{"type":"p","id":"p1","zh":"我去银行，他行不行？","segs":[
  {"en":"I'm going to the bank.","tok":[["我","wǒ"],["去","qù"],["银行","yínháng","bank"],"，"]},
  {"en":"Can he manage it?","tok":[["他","tā"],["行","xíng","to be OK"],["不","bù"],["行","xíng"],"？"]}]}
```

* **Record types:**
  * `meta`: title page.
  * `h1`: chapter heading. A chapter always starts on a new spread.
  * `h2`: section heading.
  * `p`: paragraph.
* **`zh`** is the original text, and the tokens must reproduce it exactly.
* **Tokens** are strings (punctuation), `[word, pinyin, gloss?, kind?]`, or
  `{"w":…, "py":…, "gl":…, "k":…}`.
* **Pinyin conventions:**
  * word-level, with tone marks;
  * dictionary (citation) tones, with no sandhi on 一 or 不;
  * an apostrophe before an a/o/e syllable;
  * proper names capitalised.

## Layout options (`make_book.py --help`)

| option | default | effect |
|---|---|---|
| `--paper a5\|a4` | a5 | page size. A5 gives a 21×20 grid of 5.6 mm cells; A4 gives 25×26 cells of 6.6 mm |
| `--cell MM` | 5.6 / 6.6 | Chinese cell size. The glyph is 86% of the cell |
| `--en-size PT`, `--en-lead PT` | 10/12 (A5), 11/13.5 (A4) | English type. The Chinese row pitch is `--lines-per-row` × leading |
| `--lines-per-row N` | 2 | English lines per Chinese row, so both pages share one baseline grid |
| `--margins T B I O` | 17 18 16 12 (A5) | margins in mm |
| `--para-gap N` | 1 | blank grid rows between paragraphs |
| `--gridlines box` | none | draws the cells, like 稿纸 manuscript paper |
| `--note-cols N` | 2 | footnote columns. Two columns roughly halve the space notes take |
| `--keep-words` | off | never split a word across rows (leaves empty cells instead) |
| `--no-hang` | hang | by default a closing mark that would start a row hangs in the margin; otherwise the previous character moves down |
| `--underline all\|multi\|none` | all | word underlines |
| `--annotate-above N\|none` | 4 | footnote words above HSK 3.0 level N (7 = band 7-9) |
| `--annotate-kinds NJI` | NJI | kinds that are always footnoted, unless the word is in the HSK list at or below N |
| `--scope page\|book` | page | footnote at the first occurrence on each page, or only once in the book |
| `--marks auto\|symbols\|numbers` | auto | daggers when a page has ≤ 6 notes, otherwise numbers |
| `--zh-font`, `--zh-head-font`, `--en-font` | Noto Serif CJK SC (+Bold), TeX Gyre Pagella | fonts |

## How it works

* **Fixed grid.** `zhbook/grid.py` turns tokens into cells. Each full-width character gets one cell.
  A run of half-width characters (3D, CAD, 1956, an English word) is centred over ceil(n/2) cells and
  never split. Runs longer than 8 characters are packed two per cell.
* **Line breaking:**
  * no row may start with closing punctuation or end with opening punctuation;
  * —— and …… pairs are never split;
  * a closing mark that would start a row hangs one cell into the margin, or the previous character
    moves down to the next row;
  * opening and closing quotes are aligned within their cell.
* **Paragraph sync and notes.** `zhbook/book.py` runs a quick XeLaTeX measuring pass that counts the
  lines of every English sentence range and every footnote. It then paginates spread by spread:
  * the footnotes on a Chinese page shrink the grid area of that page;
  * the English page can use its full height;
  * both members of a paragraph pair start on the same row.

  Everything is then placed with absolute coordinates, so the grid stays exact.
* **Data** (in `data/`, see its README):
  * HSK 3.0 lists (MIT). A word missing from the list gets the highest level among its characters.
  * CC-CEDICT (CC BY-SA 4.0), used to check pinyin and as a fallback for missing glosses. The
    attribution is printed when it is used.

## Limitations / ideas

* **Script and direction.** Only tested with Simplified Chinese and horizontal text. Traditional
  characters work with a TC font, but the HSK levels assume simplified forms.
* **Empty space.** The English page often has spare room, because the Chinese side usually needs more
  height. Raise `--en-size` or `--en-lead` if you prefer bigger English type.
* **Not built yet:**
  * pinyin ruby above the characters;
  * imposition for booklet printing. Any PDF imposition step (for example A5 pages onto A4
    signatures) can be run on `book.pdf`.

## Licence

* **Code** (`*.py`, `zhbook/`): MIT, see [LICENSE](LICENSE).
* **Texts and translations** (`stories/`, `examples/`, the PDFs built from them):
  [CC BY 4.0](LICENSE-TEXTS). You may share and adapt them, including commercially, if you give credit
  and link to this repository. The texts were written by an AI model. Some jurisdictions may not grant
  copyright in such text, and the licence then simply confirms that reuse is welcome.
* **Data** in `data/` keeps its own licences: the HSK 3.0 lists are MIT (© 2023 Ivan Krasilnikov), and
  CC-CEDICT is CC BY-SA 4.0. See [data/README.md](data/README.md).
* **Fonts** embedded in the PDFs: Noto Serif CJK (SIL Open Font License) and TeX Gyre Pagella (GUST
  Font License).
