#!/usr/bin/env python3
"""Run the annotation batches written by prepare.py through the Claude API.

  pip install anthropic
  export ANTHROPIC_API_KEY=...            (Windows: set ANTHROPIC_API_KEY=...)
  python annotate_api.py work/mybook [--model claude-sonnet-5-5] [--redo]

For each batches/batch_NNN.md without a matching .zhb, sends the prompt, saves
the answer as batch_NNN.zhb, converts and validates it against source.jsonl,
and retries once with the error list if the text was altered or the pinyin
is malformed. Finally writes book.jsonl. Already finished batches are skipped,
so the script can be re-run after an interruption. API use is billed to your
account.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from zhbook.checks import check_records
from zhbook.common import Record, Seg, parse_token
from zhb2jsonl import parse as parse_zhb


def to_records(raw: list[dict]) -> list[Record]:
    out = []
    for d in raw:
        if d.get("type") == "meta":
            continue
        segs = [Seg(en=s["en"], tok=[parse_token(t) for t in s["tok"]]) for s in d["segs"]]
        out.append(Record(type=d["type"], id=d["id"], zh=d["zh"], segs=segs, raw=d))
    return out


def extract_block(text: str) -> str:
    m = re.search(r"```(?:zhb)?\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workdir")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--max-tokens", type=int, default=32000)
    ap.add_argument("--redo", action="store_true", help="re-annotate batches that already have a .zhb")
    a = ap.parse_args()
    try:
        import anthropic
    except ImportError:
        print("pip install anthropic", file=sys.stderr)
        return 1
    client = anthropic.Anthropic()
    work = Path(a.workdir)
    source = {}
    for line in (work / "source.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            source[d["id"]] = d["zh"]

    def ask(messages):
        resp = client.messages.create(model=a.model, max_tokens=a.max_tokens, messages=messages)
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

    ok_all = True
    for md in sorted((work / "batches").glob("batch_*.md")):
        zhb = md.with_suffix(".zhb")
        if zhb.exists() and not a.redo:
            continue
        prompt = md.read_text(encoding="utf-8")
        ids = [json.loads(l)["id"] for l in prompt.splitlines() if l.startswith("{")]
        messages = [{"role": "user", "content": prompt}]
        for attempt in (1, 2):
            print(f"{md.name}: request {attempt} ...", flush=True)
            answer = ask(messages)
            block = extract_block(answer)
            try:
                recs = to_records(parse_zhb(block.splitlines()))
                sub = {i: source[i] for i in ids}
                errors = [str(i) for i in check_records(recs, sub) if i.level == "ERROR"]
            except SystemExit as e:              # format error raised by the parser
                errors = [str(e)]
            zhb.write_text(block, encoding="utf-8")
            if not errors:
                break
            print(f"  {len(errors)} errors", file=sys.stderr)
            messages += [{"role": "assistant", "content": answer},
                         {"role": "user", "content": "The validator found these problems. Return the corrected "
                                                     "full zhb block for all records:\n" + "\n".join(errors[:60])}]
        if errors:
            ok_all = False
            print(f"  {md.name}: still {len(errors)} errors – fix {zhb.name} by hand", file=sys.stderr)

    zhbs = sorted((work / "batches").glob("batch_*.zhb"))
    recs = []
    for z in zhbs:
        recs += parse_zhb(z.read_text(encoding="utf-8").splitlines())
    with open(work / "book.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {work / 'book.jsonl'} ({len(recs)} records)")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
