#!/usr/bin/env python3
"""Convert the compact .zhb authoring format to canonical JSONL.

  python zhb2jsonl.py text.zhb [more.zhb ...] [-o text.jsonl]

Format (UTF-8, one block per directive):

  # comment
  @meta {"title_zh": "…", "title_en": "…"}        JSON object on one line
  @h2 sec1                                        heading (also @h1), id
  春节|Chūnjié|Spring_Festival|J
  > The Spring Festival
  @p p1                                           paragraph, id
  中国|Zhōngguó 有|yǒu 很多|hěnduō 节日|jiérì 。    tokens of one aligned segment
  > China has many festivals.                     its English; closes the segment

Token = word|pinyin|gloss|kind (trailing fields optional); a bare token is
punctuation/symbols. Use '_' for spaces inside a field (Qū_Yuán). Tokens of a
segment may span several lines before the '>' line. A token without gloss or
kind inherits them from an earlier occurrence of the same word + pinyin.
"""
import argparse
import json
import sys


def parse(lines):
    recs, cur, toks = [], None, []
    known: dict = {}

    def flush_rec():
        if cur is not None:
            if toks:
                raise SystemExit(f"block {cur['id']}: tokens without a closing '>' English line")
            cur["zh"] = "".join(t if isinstance(t, str) else t[0] for s in cur["segs"] for t in s["tok"])
            recs.append(cur)

    for n, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@meta"):
            flush_rec()
            cur = None
            d = json.loads(line[5:].strip())
            d["type"] = "meta"
            recs.append(d)
            continue
        if line.startswith("@"):
            flush_rec()
            typ, _, rid = line[1:].partition(" ")
            cur = {"type": typ, "id": rid.strip() or f"r{n}", "segs": []}
            continue
        if cur is None:
            raise SystemExit(f"line {n}: content before any @p/@h directive")
        if line.startswith(">"):
            if not toks:
                raise SystemExit(f"line {n}: English line without tokens")
            cur["segs"].append({"en": line[1:].strip(), "tok": toks})
            toks = []
            continue
        for item in line.split():
            f = [x.replace("_", " ") for x in item.split("|")]
            if len(f) == 1:
                toks.append(f[0])
                continue
            while len(f) < 4:
                f.append("")
            w, py, gl, k = f[:4]
            key = (w, py)
            if key in known:
                gl = gl or known[key][0]
                k = k or known[key][1]
            if gl or k:
                known[key] = (gl, k)
            tok = [w, py] + ([gl] if gl or k else []) + ([k] if k else [])
            toks.append(tok)
    flush_rec()
    return recs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="+")
    ap.add_argument("-o", "--out", help="output .jsonl (default: alongside a single source)")
    a = ap.parse_args()
    if len(a.src) > 1 and not a.out:
        ap.error("-o is required with several inputs")
    recs = []
    for src in a.src:
        with open(src, encoding="utf-8") as f:
            recs += parse(f)
    out = a.out or a.src[0].rsplit(".", 1)[0] + ".jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {len(recs)} records to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
