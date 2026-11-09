You are annotating Chinese text for a dual-language (Chinese/English) reader for learners.
Return the annotation in the **zhb format** described below, inside one ```zhb code block, and nothing else.

## zhb format

```
@p <id>                      (or @h1 <id> / @h2 <id> for headings; keep the ids and types given)
<tokens of segment 1>
> <English of segment 1>
<tokens of segment 2>
> <English of segment 2>
```

* A **token** is `word|pinyin|gloss|kind`; trailing fields may be omitted (`word|pinyin`).
  Punctuation and symbols are bare tokens (`，` `。` `“`), separated by spaces like everything else.
* Inside a field, write `_` instead of a space (`Qū_Yuán`, `to_pay_a_visit`). Never use `|` inside a field.
* A **segment** is one or more sentences whose Chinese and English correspond. Its tokens may run over
  several lines; the `> English` line closes it.

## Rules

1. **Never change the Chinese.** Concatenating all token words of a record must reproduce the source text
   exactly, character for character: same punctuation (full-width stays full-width), same quotes, same
   digits and Latin letters, no added or removed characters. A script checks this and rejects the record.
2. **Segmentation:** split into dictionary words as in CC-CEDICT (e.g. 中秋节, 年夜饭, 一起, 为了). Keep
   grammatical particles (的, 了, 着, 过, 地, 得) and measure words as separate tokens. Keep names and set
   phrases (chengyu) as one token.
3. **Pinyin:** tone marks (ā á ǎ à, ü), written as one word without spaces (`Zhōngqiūjié`, `yīqǐ`);
   multi-word names/idioms with `_` (`Qū_Yuán`, `chángshēng_bùlǎo`). Use **dictionary (citation) tones**:
   no tone-sandhi changes for 一 and 不; neutral tone written unmarked where the dictionary has it
   (`dōngxi`, `xǐhuan`). Use an apostrophe before a syllable starting with a/o/e (`Cháng'é`, `Xī'ān`).
   Capitalise proper names. Pick the reading the context requires for polyphonic characters (行, 长, 重,
   得, 还, 了 …).
4. **Gloss:** short English meaning *in this context*, at most ~6 words. Give a gloss for every word that
   is not basic (roughly above HSK 3) and for every name, term and idiom. Basic words may omit it.
5. **Kind:** `N` = proper name (people, places, states, deities, works); `J` = domain term or cultural
   item (festival names, foods, customs, technical vocabulary); `I` = chengyu, proverb or set phrase.
   Leave empty otherwise.
6. **Segments and English:**
   * If an English translation is supplied, **do not rewrite it**. Only distribute it over segments,
     splitting at sentence boundaries. If one English sentence covers several Chinese sentences (or the
     reverse), put them together in one segment.
   * If no translation is supplied, translate faithfully into natural, fluent English, one segment per
     Chinese sentence (or small group of sentences).
7. Annotate every record you are given, in order, keeping its id and type. Do not add commentary.

## Example

Source record: `{"id": "p12", "type": "p", "zh": "我去银行，他行不行？"}`

```zhb
@p p12
我|wǒ 去|qù 银行|yínháng|bank ，
> I'm going to the bank.
他|tā 行|xíng|to_be_OK 不|bù 行|xíng ？
> Can he manage it?
```
