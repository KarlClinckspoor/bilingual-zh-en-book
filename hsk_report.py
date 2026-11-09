#!/usr/bin/env python3
"""Report the HSK 3.0 level profile of an annotated text.

  python hsk_report.py book.jsonl [--target 4] [--list]

Counts running word tokens (names excluded) and distinct words per level.
Words missing from the official word list get the highest level among their
characters ("~" in the listing); '?' means a character is outside HSK.
"""
import argparse
from collections import Counter

from zhbook.common import hsk_level, load_records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--target", type=int, default=4, help="level the text aims at (default 4)")
    ap.add_argument("--list", action="store_true", help="list every distinct word above target")
    a = ap.parse_args()

    recs = load_records(a.files)
    running: Counter = Counter()
    distinct: dict[str, tuple] = {}
    names = set()
    nchars = 0
    for r in recs:
        for s in r.segs:
            for t in s.tok:
                if not t.has_hanzi:
                    continue
                nchars += len(t.w)
                if t.k == "N":
                    names.add(t.w)
                    continue
                lv, how = hsk_level(t.w)
                key = lv if lv is not None else 99
                running[key] += 1
                distinct[t.w] = (key, how, t.k, t.py, t.gl)

    total = sum(running.values())
    dcount = Counter(v[0] for v in distinct.values())
    dtotal = len(distinct)
    print(f"{nchars} hanzi, {total} word tokens, {dtotal} distinct words, {len(names)} names (excluded)\n")
    print("level      tokens   cum%   distinct   cum%")
    ct = cd = 0
    for lv in sorted(running):
        ct += running[lv]
        cd += dcount[lv]
        label = {7: "7-9", 99: "beyond"}.get(lv, str(lv))
        print(f"HSK {label:6s} {running[lv]:6d} {100*ct/total:6.1f}  {dcount[lv]:8d} {100*cd/dtotal:6.1f}")
    above = sorted(((v[0], w, v) for w, v in distinct.items() if v[0] > a.target))
    at_or_below = sum(running[l] for l in running if l <= a.target)
    print(f"\n{100*at_or_below/total:.1f}% of running words are at or below HSK {a.target}; "
          f"{len(above)} distinct words above it.")
    if a.list or len(above) <= 80:
        print()
        for lv, w, (key, how, k, py, gl) in above:
            label = {7: "7-9", 99: "?"}.get(lv, str(lv))
            mark = "~" if how == "chars" else " "
            print(f"  HSK {label:3s}{mark} {k or '-'} {w}\t{py}\t{gl}")


if __name__ == "__main__":
    main()
