# Writing brief: HSK 1, 2, 3 and 6 stories (22–61)

This brief is for the writer of one or more stories in the HSK 1, 2, 3 and 6 series. The project
lives in `C:\Users\karl9\Downloads\Claude\bilingual-zh-en-book`. Run every command from there.

## Read first
1. **The plan for your level**, and in it your story's section (content, plot, sections, grammar):
   `plans/hsk1-stories.md`, `plans/hsk2-stories.md`, `plans/hsk3-stories.md` or `plans/hsk6-stories.md`.
2. `prompts/annotate.md`: the zhb token format and the annotation rules (segmentation, pinyin, gloss, kind).
3. `README.md`, section "Formats": the `.zhb` syntax, including `@meta`, `@h2`, `@p` and inheritance.
4. A finished example of the house style: `stories/hsk5/21-moon/21-moon.zhb` (header comment,
   `@meta`, `@h2` and `@p` ids, glosses, N/J/I kinds).

## What to produce
For each story you are given:
- `stories/hsk<L>/<NN-slug>/<NN-slug>.zhb`: an **original text you write yourself**, in Chinese,
  fully annotated, with the English translation in the `> ` lines.
- `stories/hsk<L>/<NN-slug>/<NN-slug>.jsonl`, generated with `zhb2jsonl.py`.
- **Do not build the PDF.** It is built later, centrally.
- Touch no other files: no other stories, no README, no plans, no code, and no git commands.

## Targets by level

| | HSK 1 | HSK 2 | HSK 3 | HSK 6 |
|---|---|---|---|---|
| length (hanzi, punctuation excluded) | 400–700 | 800–1,200 | 1,300–1,900 | 3,800–4,800 |
| `@h2` sections | 2–3 | 3–4 | 3–5 | 6–9 |
| paragraph size (hanzi) | 30–80 | 40–110 | 50–150 | 80–220 |
| vocabulary rule | **100 %** at ≤ HSK 1 | **100 %** at ≤ HSK 2 | ≥ 92 % at ≤ HSK 3 | ≥ 90 % at ≤ HSK 6 |
| kinds allowed | **N only** | **N only** | N, J, I | N, J, I |
| `--annotate-above` | 1 | 2 | 3 | 6 |

### HSK 1 and HSK 2: the strict rule
The reader is expected to know **every word and character in the HSK list up to the level**, and
nothing else. Only names get footnotes. So:
- **Every token that is not a name must be at or below the level** in `hsk_report.py`. This counts
  a word as known if it is in the word list at that level, or if it is missing from the list but all
  of its characters are in the character list at that level. The target is `100.0%` and
  `0 distinct words above it`. **No exceptions**: write around any word that is above the level.
- **No `J` and no `I` tokens.** Only `N`, and only for real proper names (people, places,
  rivers, works). Never mark an ordinary word as `N` to get it past the check.
- Use few names, and short ones: two or three people per story, plus places the plot needs. Each name
  needs a gloss (it becomes a footnote). Family words (妈妈, 爷爷) are not names.
- **Segment carefully.** Split into list words. If a compound is above the level but its parts
  are both list words and the split is natural Chinese (e.g. 吃 + 饭 rather than an unusual
  compound), split it. Do not split real words just to dodge the check. Choose a different word instead.
- Useful check: `python -c "from zhbook.common import hsk_level; print(hsk_level('猫'))"` prints
  `(level, 'word'|'chars'|'none')` for any word before you use it.
- **Style:** short sentences, a lot of natural repetition, simple dialogue. It must still read as a
  real little text with a point or a small surprise at the end, not a list of sentences.

### HSK 3 and HSK 6
- Everything above the level should be a name (N), a term (J) or an idiom (I), or be truly needed.
  Run `--list` and replace replaceable words above the level with simpler ones.
- **HSK 6:** words the list puts at **7–9** (for example 何况, 与其, 宁可, 以致, 并非, 竟, 何必,
  固然) may appear but are **not** focus points. When they appear they get a gloss and are footnoted.
  A few classical quotations are welcome. Each is one `I` token, or short tokens with glosses, and the
  English gives a translation.

## Story requirements (all levels)
- **Form:** follow the plot, the sections and the ending idea in the plan. You may change details if
  the story reads better.
  - One `> English` segment per sentence or small sentence group.
  - Dialogue in Chinese quotes “……”. Opening and closing quotes are separate bare tokens (“ and ”).
- **Grammar:** use each **focus point** in the plan several times (HSK 1–2: 2–4 times, HSK 3: 3–5,
  HSK 6: 3–5), in both narration and dialogue. Write naturally: the grammar serves the story.
- **Content:**
  - For history and science stories, keep facts right. Where something is uncertain (numbers,
    dates), say so (据说, 大约, 有人认为…) or leave it vague.
  - No medical advice (stories 27, 58).
  - Real living people (58) are treated respectfully and only with well-documented facts.
- **Header:** two `#` comment lines, e.g.
  `# <English title> — original story and translation by Claude (Anthropic).` and
  `# Target: HSK 3.0 level <L>; focus grammar: …; names N[, terms J, set phrases I].`
- **Meta:**
  `@meta {"title_zh": "…", "subtitle_zh": "…", "title_en": "…", "subtitle_en": "…", "author": "Text and translation by Claude (Anthropic)"}`.
  Write a short subtitle in both languages. At HSK 1 and 2 the Chinese title and subtitle obey the
  vocabulary rule too.
- **Ids:** the first paragraph is `intro` or similar. Sections are `h-<word>`, and their paragraphs
  are `<word>-1`, `<word>-2`…, as in the example. Ids are unique within a file.

## Annotation requirements (prompts/annotate.md, plus)
- Every token is `word|pinyin` at least, and the words must reproduce the Chinese exactly.
- **Gloss:**
  - HSK 1–2: a gloss for every name (required). Other glosses are optional; they are not printed.
  - HSK 3: a gloss for every word above HSK 3 and for every name, term and idiom.
  - HSK 6: a gloss for every word above HSK 5 and for every name, term and idiom.
  - Keep glosses short (≤ 6 words) and right for the context.
- **Pinyin:** citation tones, with no sandhi on 一 or 不. Neutral tones as in the dictionary,
  apostrophe before a/o/e syllables, names capitalised. Directional complements in neutral tone
  (*qǐlai, chūlai, xiàqu*) as in the HSK 4/5 house style.
- **Translation:** natural, fluent English that is faithful to the Chinese. At HSK 1–2 the English
  may be simple, but not broken.

## Check loop (repeat until clean)
```bash
export PYTHONIOENCODING=utf8
python zhb2jsonl.py stories/hsk<L>/<NN-slug>/<NN-slug>.zhb
python validate.py stories/hsk<L>/<NN-slug>/<NN-slug>.jsonl --annotate-above <L>
python hsk_report.py stories/hsk<L>/<NN-slug>/<NN-slug>.jsonl --target <L> --list
```
- Fix **all ERRORs**.
- For each pinyin **WARN**, either fix it or, if you are sure the context reading is right, leave it
  and list it in your report.
- INFO lines (neutral-tone differences) may stay.
- HSK 1–2: the report must say `100.0% of running words are at or below HSK <L>; 0 distinct words above it.`
- Count hanzi with the first line of `hsk_report.py` ("N hanzi").

**Tip:** for long files, write section by section (create the file with the first sections, then
append) and run the check loop after each section or two, so errors stay small.

## Report back (short, per story)
- File paths, hanzi count, % at ≤ level, and the number of distinct words above the level.
- Each focus grammar point: how many times it is used, with one example sentence.
- The list of N tokens (HSK 1–2).
- Remaining WARNs (with why the reading is right), and any facts you were unsure of.
