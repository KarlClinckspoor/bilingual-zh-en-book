# Writing brief for one HSK 5 story

This brief is for the writer of **one** story in the HSK 5 series (stories 12–21). The project
lives in `C:\Users\karl9\Downloads\Claude\bilingual-zh-en-book`. Run every command from there.

## Read first
1. `plans/hsk5-stories.md`: targets, the grammar map, and **your story's section** (content, plot,
   section titles, vocabulary field, fact-check notes).
2. `prompts/annotate.md`: the zhb token format and annotation rules (segmentation, pinyin, gloss, kind).
3. `README.md`, section "Formats": the `.zhb` syntax, including `@meta`, `@h2`, `@p` and inheritance.
4. `stories/hsk4/11-qin-shi-huang/11-qin-shi-huang.zhb`: a finished example of the house style
   (header comment, `@meta`, `@h2` and `@p` ids, glosses, N/J/I kinds).

## What to produce
- `stories/hsk5/<NN-slug>/<NN-slug>.zhb`, an **original story you write yourself**, in Chinese,
  fully annotated, with the English translation in the `> ` lines.
- `stories/hsk5/<NN-slug>/<NN-slug>.jsonl`, generated with `zhb2jsonl.py`.
- **Do not build the PDF.** It is built later, centrally.
- Touch no other files: no other stories, no README, no plans, and no git commands.

## Story requirements
- **Length:** 2,800–3,500 hanzi (Chinese characters only, punctuation excluded).
- **Form:** a narrative short story with characters and dialogue (use “……” quotes), following the
  plot and section titles in the plan. You may adjust details if the story reads better, but keep the
  content, the arc and the ending idea.
  - 5–8 `@h2` sections.
  - Paragraphs of about 60–200 hanzi.
  - One `> English` segment per sentence or small sentence group.
- **Level:**
  - `hsk_report.py --target 5` must show **≥ 90 %** of running words at or below HSK 5.
  - Everything above level 5 should be a name (N), a term (J) or an idiom (I), or be truly needed.
  - Run `--list` and replace replaceable words above HSK 5 with simpler ones.
- **Grammar:**
  - Use each of your 4 **focus points** (from the grammar map) **3–5 times**, in both narration and
    dialogue.
  - Use each **review point** at least once.
  - Write it naturally. The grammar must serve the story, not the reverse.
- **Content:**
  - Accurate cultural and historical detail.
  - For the history and science stories, keep facts right. Where something is uncertain (numbers,
    dates), say so in the text (据说, 大约, 有人认为…) or leave it vague.
  - No medical advice in story 20.
- **Header:** two `#` comment lines like the example, e.g.
  `# <English title> — original story and translation by Claude (Anthropic).` and
  `# Target: HSK 3.0 level 5; focus grammar: …; names N, terms J, set phrases I.`
- **Meta:**
  `@meta {"title_zh": "…", "subtitle_zh": "…", "title_en": "…", "subtitle_en": "…", "author": "Text and translation by Claude (Anthropic)"}`.
  Write a short, evocative subtitle in both languages.
- **Ids:** the first paragraph is `intro` or similar. Sections are `h-<word>`, and their paragraphs
  are `<word>-1`, `<word>-2`…, as in the example.

## Annotation requirements (prompts/annotate.md, plus)
- Every token is `word|pinyin` at least, and the words must reproduce the Chinese exactly.
- **Gloss:** give one for every word above HSK 4, and for every name, term and idiom. Keep glosses
  short and right for the context.
- **Kind:** `N` for names (including the main characters' names), `J` for cultural or technical
  terms, `I` for chengyu and set phrases.
- **Pinyin:** citation tones, with no sandhi on 一 or 不. Neutral tones as in the dictionary,
  apostrophe before a/o/e syllables, names capitalised.
- **Translation:** natural, fluent English that is faithful to the Chinese.
- **Quotes:** opening and closing Chinese quotes are separate bare tokens (“ and ”).

## Check loop (repeat until clean)
```bash
export PYTHONIOENCODING=utf8
python zhb2jsonl.py stories/hsk5/<NN-slug>/<NN-slug>.zhb
python validate.py stories/hsk5/<NN-slug>/<NN-slug>.jsonl --annotate-above 5
python hsk_report.py stories/hsk5/<NN-slug>/<NN-slug>.jsonl --target 5 --list
```
- Fix **all ERRORs**.
- For each pinyin **WARN**, either fix it or, if you are sure the context reading is right, leave it
  and list it in your report.
- INFO lines (neutral-tone differences) may stay.

**Tip:** the file is long. Write it section by section (create the file with the first sections, then
append), and run the check loop after each section or two, so errors stay small.

## Report back (short)
- File paths, hanzi count, % at ≤ HSK 5, and the number of distinct words above HSK 5.
- For each focus grammar point: how many times it is used, with one example sentence.
- Remaining WARNs (with why the reading is right), and any facts you were unsure of.
