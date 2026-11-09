#!/usr/bin/env python3
"""Prepare an existing Chinese text (optionally with its translation) for annotation.

  python prepare.py original.txt [--en translation.txt] -o work/mybook
                    [--batch-chars 1500] [--title-zh … --title-en … --author …]

Input text: paragraphs separated by blank lines (or one paragraph per line if
the file has no blank lines). Lines starting with '# ' are chapter headings
(h1), '## ' section headings (h2). The English file, if given, must have the
same structure and the same number of paragraphs.

Writes into the output folder:
  source.jsonl        the paragraphs with ids – the reference for validate.py --source
  meta.jsonl          title page information (if given)
  batches/batch_NNN.md   prompt + records, ready to paste into Claude
                         (or to run with annotate_api.py)

Then save each answer as batches/batch_NNN.zhb and run:
  python zhb2jsonl.py work/mybook/batches/*.zhb -o work/mybook/book.jsonl
  python validate.py work/mybook/book.jsonl --source work/mybook/source.jsonl
  python make_book.py work/mybook/meta.jsonl work/mybook/book.jsonl -o work/mybook/build
"""
import argparse
import json
import re
import sys
from pathlib import Path

from zhbook.common import ROOT, count_hanzi


def read_blocks(path: str) -> list[tuple[str, str]]:
    text = Path(path).read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    if re.search(r"\n\s*\n", text):
        parts = [re.sub(r"\s*\n\s*", "", p.strip()) if not p.strip().startswith("#") else p.strip()
                 for p in re.split(r"\n\s*\n", text)]
    else:
        parts = [line.strip() for line in text.split("\n")]
    out = []
    for p in parts:
        if not p:
            continue
        if p.startswith("## "):
            out.append(("h2", p[3:].strip()))
        elif p.startswith("# "):
            out.append(("h1", p[2:].strip()))
        else:
            out.append(("p", p))
    return out


def read_en_blocks(path: str) -> list[tuple[str, str]]:
    text = Path(path).read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    if re.search(r"\n\s*\n", text):
        parts = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text)]
    else:
        parts = [line.strip() for line in text.split("\n")]
    out = []
    for p in parts:
        if not p:
            continue
        typ = "h2" if p.startswith("## ") else "h1" if p.startswith("# ") else "p"
        out.append((typ, p.lstrip("#").strip()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zh")
    ap.add_argument("--en", help="existing English translation (same paragraph structure)")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--batch-chars", type=int, default=1500, help="approx. hanzi per batch (default 1500)")
    ap.add_argument("--title-zh")
    ap.add_argument("--title-en")
    ap.add_argument("--subtitle-zh")
    ap.add_argument("--subtitle-en")
    ap.add_argument("--author")
    a = ap.parse_args()

    zh = read_blocks(a.zh)
    en = read_en_blocks(a.en) if a.en else None
    if en is not None and len(en) != len(zh):
        print(f"paragraph count differs: {len(zh)} Chinese vs {len(en)} English blocks. "
              f"Fix the files so blocks correspond one to one.", file=sys.stderr)
        return 1

    out = Path(a.out)
    (out / "batches").mkdir(parents=True, exist_ok=True)
    recs, counters = [], {"p": 0, "h1": 0, "h2": 0}
    for i, (typ, text) in enumerate(zh):
        counters[typ] += 1
        r = {"id": f"{typ}{counters[typ]:04d}", "type": typ, "zh": text}
        if en is not None:
            r["en"] = en[i][1]
        recs.append(r)
    with open(out / "source.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {k: getattr(a, k) for k in ("title_zh", "title_en", "subtitle_zh", "subtitle_en", "author") if getattr(a, k)}
    if meta:
        meta["type"] = "meta"
        (out / "meta.jsonl").write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")

    prompt = (ROOT / "prompts" / "annotate.md").read_text(encoding="utf-8")
    batches, cur, size = [], [], 0
    for r in recs:
        n = count_hanzi(r["zh"])
        if cur and size + n > a.batch_chars:
            batches.append(cur)
            cur, size = [], 0
        cur.append(r)
        size += n
    if cur:
        batches.append(cur)
    for bi, batch in enumerate(batches, 1):
        lines = [prompt, "", "## Records to annotate", "",
                 "English translation supplied: " + ("yes – distribute it, do not rewrite it." if en else "no – translate."), ""]
        lines += [json.dumps(r, ensure_ascii=False) for r in batch]
        (out / "batches" / f"batch_{bi:03d}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    total = sum(count_hanzi(r["zh"]) for r in recs)
    print(f"{len(recs)} records, {total} hanzi -> {len(batches)} batches in {out / 'batches'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
