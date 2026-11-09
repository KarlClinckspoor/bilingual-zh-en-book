# Plan: publishing the stories on GitHub

## The two options

| | A · zip files in Releases | B · stories in the repository, by HSK level and theme |
|---|---|---|
| reader gets | one download per level (all PDFs) | browse, preview and link any single PDF in the browser |
| discoverability | low: readers must find the Releases tab | high: the README shows a catalogue, and search engines index the files |
| versions | each release is a fixed, numbered snapshot (`v1.0`) | always the latest version. History is in git, but readers don't see "editions" |
| corrections | fixed in the next release | a reader can point to the exact line in a `.zhb` and open an issue or PR |
| repo size | small: PDFs stay out of git history | grows with every rebuilt PDF (~200 KB each, so 100 stories ≈ 20 MB plus rebuilds. Fine) |
| work per update | build the zip, make a release | commit, then update the README table |

Neither is wrong. **A** suits people who want "the book". **B** suits people who want to read one story
now or help fix it.

## Recommendation: B as the base, A on top

1. **Keep every story in the repository**, with its source and PDF together, so it can be browsed and
   corrected.
2. **Organise folders by level only.** Theme is a *tag* in the catalogue, not a folder (see why below).
3. **Publish a release for each finished level**, with one zip containing the PDFs, a short reader's
   README and the licence. This gives the "download the whole set" experience without a second source
   of truth.

### Folder layout

```
stories/
  README.md                ← full catalogue: every story with level, themes, length, grammar focus
  hsk4/
    README.md              ← table for this level only
    01-tea/
      01-tea.zhb           ← source (edit this)
      01-tea.jsonl         ← generated
      01-tea.pdf           ← generated
    02-regional-food/ …
  hsk5/
    README.md
    12-watch-repairer/ …
plans/                     ← writing plans (hsk5-stories.md, this file)
examples/festivals/        ← tool demo, stays where it is
zhbook/, *.py, data/       ← the tool
```

* **Why not `hsk5/history/13-zheng-he/`?** Many stories have two themes (09 is both history and science,
  06 is language and daily life). A theme folder forces one choice, leaves folders with only one or two
  stories, and moving a story later breaks every link to it. A tag column in the README costs nothing
  and can list several themes.
* **Numbers stay global** (01–21, then 22…), so "story 12" always means the same text at every level.
* **Theme tags** (fixed list, so tables stay consistent): `culture & daily life` · `history` ·
  `language` · `nature & environment` · `science & technology` · `tradition & ideas` · `society`.

If you prefer theme folders anyway, use `stories/hsk5/<theme>/<story>/` with the *main* theme only, and
keep the tag column for the others.

### Release contents

```
hsk4-stories-v1.0.zip
  README.txt          ← what the PDFs are, how to read them, credit line, link to the repo
  LICENSE-TEXTS.txt
  01-tea.pdf … 11-qin-shi-huang.pdf
```

* **Versioning:** one tag per level edition: `hsk4-v1.0`, later `hsk5-v1.0`. A typo fix gives
  `hsk4-v1.1`.
* **Optional:** one combined PDF per level (an "anthology") in the same release. `make_book.py` takes
  several `.jsonl` files, so a combined book is one command. Check that the chapter breaks come out as
  wanted.

## Steps

**Chosen:** level folders in the repository, plus a release zip per level.

### 1. Local preparation (done)
- `.gitignore` · `LICENSE` (MIT, code) · `LICENSE-TEXTS` (CC BY 4.0, texts) · licence section and story
  catalogue in `README.md` · local `git init` and first commit.

### 2. Move to the level layout (done)
`texts/*` moved to `stories/hsk4/`. Added `stories/README.md` (all levels), `stories/hsk4/README.md` and
`stories/hsk5/README.md` (planned list). Links updated and checked.

### 3. Create the GitHub repository (needs your go-ahead)
```bash
gh repo create bilingual-zh-en-book --private --source . --push \
  --description "Graded Chinese–English facing-page readers (HSK 3.0) and the tool that builds them"
```
Start **private** and look at it on GitHub (do the README, PDF previews and links work?), then switch
to public:
```bash
gh repo edit --visibility public --accept-visibility-change-consequences
```
Add topics so learners can find it: `chinese` `mandarin` `hsk` `graded-readers` `language-learning`
`bilingual` `xelatex`.

### 4. First release (zip built; upload needs your go-ahead)
```bash
python make_release.py hsk4 v1.0          # → dist/hsk4-stories-v1.0.zip (done, 2.1 MB)
gh release create hsk4-v1.0 dist/hsk4-stories-v1.0.zip \
  --title "HSK 4 stories, v1.0" \
  --notes "Eleven Chinese/English facing-page readers at HSK 3.0 level 4. Download the zip, or read single PDFs in stories/hsk4."
```
`make_release.py` writes the reader's `README.txt` (story list, credit, licence) and adds
`LICENSE-TEXTS.txt` and all PDFs of the level. `dist/` is ignored by git, so the zip lives only in the
release. If the repository gets a different name, pass `--repo <url>` so the links inside README.txt
are right.

### 5. Each new HSK 5 story
1. Write `stories/hsk5/NN-slug/NN-slug.zhb`, run validate, hsk_report and make_book.
2. Add a row to `stories/hsk5/README.md` and `stories/README.md`.
3. Commit and push. The story is readable on GitHub at once.
4. When all ten are finished, make release `hsk5-v1.0`.

### Later (optional)
- **GitHub Pages:** a simple website listing the stories, built from the same README tables.
- **GitHub Actions:** rebuild the PDFs automatically on every push (needs XeLaTeX and Noto CJK in CI,
  which is possible but slow), and attach the zips to releases automatically.
- **Issue template "Report a mistake":** fields for story number, paragraph id (e.g. `rise-1`), and
  what is wrong (Chinese, pinyin, translation).

## Before going public: checklist
- [ ] A native speaker has read at least a sample of the HSK 4 texts.
- [ ] The README "About the texts" note (AI-written, may contain errors) is visible.
- [ ] Every PDF opens and previews in GitHub's viewer.
- [ ] There is nothing private in the files (paths, names, API keys). `git grep -i "api_key\|C:/Users"`.
- [ ] Choose a repository name. Suggestions: `bilingual-zh-en-book` (current folder), `hsk-graded-readers`,
      `zhbook`.
