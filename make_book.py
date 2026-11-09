#!/usr/bin/env python3
"""Lay out annotated JSONL as a dual-language book (Chinese left, English right).

  python make_book.py book.jsonl [more.jsonl ...] -o build/mybook [options]

Produces build/mybook/book.tex and (unless --no-pdf) book.pdf via XeLaTeX.
Run validate.py first; this script assumes the input is clean.
"""
import argparse
import sys
from pathlib import Path

from zhbook.book import PAPERS, BookBuilder, Config, run_xelatex
from zhbook.checks import check_records
from zhbook.common import load_records


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("-o", "--out", default="build/book", help="output directory (default build/book)")
    g = ap.add_argument_group("page geometry")
    g.add_argument("--paper", choices=sorted(PAPERS), default="a5")
    g.add_argument("--cell", type=float, help="Chinese cell size in mm (A5 default 5.6, A4 6.6)")
    g.add_argument("--en-size", type=float, help="English font size in pt")
    g.add_argument("--en-lead", type=float, help="English leading in pt; row pitch = lines-per-row x this")
    g.add_argument("--lines-per-row", type=int, default=2, help="English lines per Chinese row (default 2)")
    g.add_argument("--margins", type=float, nargs=4, metavar=("TOP", "BOTTOM", "INNER", "OUTER"))
    g.add_argument("--para-gap", type=int, default=1, help="blank rows between paragraphs (default 1)")
    g.add_argument("--gridlines", choices=["none", "box"], default="none", help="draw manuscript-paper cells")
    g.add_argument("--note-cols", type=int, default=2, help="footnote columns (default 2)")
    g.add_argument("--no-hang", action="store_true", help="never hang punctuation in the margin")
    g.add_argument("--keep-words", action="store_true", help="avoid splitting words across rows")
    g.add_argument("--no-para-numbers", action="store_true")
    a2 = ap.add_argument_group("reading aids")
    a2.add_argument("--underline", choices=["all", "multi", "none"], default="all",
                    help="underline every word, only multi-character words, or none")
    a2.add_argument("--annotate-above", default="4",
                    help="footnote words above this HSK 3.0 level (1-6, 7 = band 7-9; 'none' = off)")
    a2.add_argument("--annotate-kinds", default="NJI",
                    help="token kinds always footnoted: N=names J=jargon I=idioms (default NJI, '' = none)")
    a2.add_argument("--scope", choices=["page", "book"], default="page",
                    help="footnote a word at its first occurrence per page (default) or per book")
    a2.add_argument("--marks", choices=["auto", "symbols", "numbers"], default="auto",
                    help="auto = daggers (†‡§¶*#) when a page has ≤6 notes, else numbers")
    f = ap.add_argument_group("fonts")
    f.add_argument("--zh-font", default="Noto Serif CJK SC")
    f.add_argument("--zh-head-font", default="Noto Serif CJK SC Bold")
    f.add_argument("--en-font", default="TeX Gyre Pagella")
    ap.add_argument("--no-pdf", action="store_true", help="only write the .tex")
    ap.add_argument("--force", action="store_true", help="build even if validation finds errors")
    a = ap.parse_args()

    recs = load_records(a.files)
    errors = [i for i in check_records(recs, use_cedict=False) if i.level == "ERROR"]
    if errors:
        for e in errors[:20]:
            print(e, file=sys.stderr)
        if not a.force:
            print(f"{len(errors)} validation errors; fix them or use --force", file=sys.stderr)
            return 1

    kw = dict(paper=a.paper, k=a.lines_per_row, para_gap=a.para_gap, gridlines=a.gridlines, note_cols=a.note_cols,
              hang=not a.no_hang, keep_words=a.keep_words, para_numbers=not a.no_para_numbers,
              underline=a.underline, annotate_kinds=a.annotate_kinds, scope=a.scope, marks=a.marks,
              annotate_above=None if a.annotate_above.lower() == "none" else int(a.annotate_above),
              zh_font=a.zh_font, zh_head_font=a.zh_head_font, en_font=a.en_font)
    for name in ("cell", "en_size", "en_lead"):
        if getattr(a, name):
            kw[name] = getattr(a, name)
    if a.margins:
        kw.update(top=a.margins[0], bottom=a.margins[1], inner=a.margins[2], outer=a.margins[3])
    cfg = Config(**kw)

    out = Path(a.out)
    builder = BookBuilder(recs, cfg, out)
    tex = builder.build_tex()
    (out / "book.tex").write_text(tex, encoding="utf-8")
    n_pages = 1 + 2 * len(builder.pages)
    print(f"grid {cfg.cols} x {cfg.rows} cells of {cfg.cell} mm, row pitch {cfg.P:.2f} mm; "
          f"{len(builder.pages)} spreads ({n_pages} pages)")
    for w in builder.warnings:
        print("warning:", w, file=sys.stderr)
    if not a.no_pdf:
        run_xelatex(out, "book.tex")
        for ext in ("aux", "log", "mes", "xdv"):
            for p in out.glob(f"*.{ext}"):
                p.unlink()
        print(f"wrote {out / 'book.pdf'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
