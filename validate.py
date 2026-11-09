#!/usr/bin/env python3
"""Validate annotated JSONL files.

  python validate.py book.jsonl [more.jsonl ...] [--source source.jsonl]
                     [--annotate-above 4] [--no-cedict] [--quiet]

Exit status 1 if any ERROR was found.
"""
import argparse
import json
import sys

from zhbook.checks import check_records
from zhbook.common import load_records


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--source", help="source.jsonl written by prepare.py; checks text was not altered")
    ap.add_argument("--annotate-above", type=int, default=None, metavar="N",
                    help="warn about words above HSK N that lack a gloss")
    ap.add_argument("--no-cedict", action="store_true", help="skip CC-CEDICT pinyin cross-check")
    ap.add_argument("--quiet", "-q", action="store_true", help="hide INFO lines")
    a = ap.parse_args()

    recs = load_records(a.files)
    source = None
    if a.source:
        source = {}
        with open(a.source, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    source[str(d["id"])] = d["zh"]
    issues = check_records(recs, source, a.annotate_above, not a.no_cedict)
    for i in issues:
        if a.quiet and i.level == "INFO":
            continue
        print(i)
    n_err = sum(i.level == "ERROR" for i in issues)
    n_warn = sum(i.level == "WARN" for i in issues)
    ntok = sum(len(s.tok) for r in recs for s in r.segs)
    print(f"\n{len(recs)} records, {ntok} tokens: {n_err} errors, {n_warn} warnings", file=sys.stderr)
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
