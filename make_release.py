#!/usr/bin/env python3
"""Bundle one level's PDFs into a release zip.

    python make_release.py hsk4 v1.0
    → dist/hsk4-stories-v1.0.zip  (README.txt, LICENSE-TEXTS.txt, NN-slug.pdf …)

Upload the zip with:  gh release create hsk4-v1.0 dist/hsk4-stories-v1.0.zip --title "…" --notes "…"
"""
import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

README = """\
{heading}
{rule}

{count} texts. Each PDF has Chinese on the left page and English on the right.
Word boundaries are underlined; names, special terms and words above the
target level are footnoted with pinyin and meaning.

{listing}

Texts and translations by Claude (Anthropic), an AI model. They have been
checked with automatic tools but may still contain mistakes. Corrections are
welcome: {repo}/issues

Licence: CC BY 4.0 (see LICENSE-TEXTS.txt). You may share and adapt these
texts, including commercially, if you give credit and link to
{repo}
Fonts: Noto Serif CJK (SIL OFL), TeX Gyre Pagella (GUST Font License).
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("level", help="folder under stories/, e.g. hsk4")
    ap.add_argument("version", help="e.g. v1.0")
    ap.add_argument("--repo", default="https://github.com/KarlClinckspoor/bilingual-zh-en-book")
    ap.add_argument("-o", "--out", default=str(ROOT / "dist"))
    a = ap.parse_args()

    level_dir = ROOT / "stories" / a.level
    stories = sorted(p for p in level_dir.iterdir() if p.is_dir())
    entries = []
    for d in stories:
        pdf = d / f"{d.name}.pdf"
        if not pdf.exists():
            raise SystemExit(f"missing PDF: {pdf}  (build it with make_book.py first)")
        meta = {}
        jsonl = d / f"{d.name}.jsonl"
        if jsonl.exists():
            first = json.loads(jsonl.read_text(encoding="utf-8").splitlines()[0])
            if first.get("type") == "meta":
                meta = first
        entries.append((pdf, meta))
    if not entries:
        raise SystemExit(f"no stories in {level_dir}")

    title = "HSK " + a.level.removeprefix("hsk") if a.level.startswith("hsk") else a.level
    listing = "\n".join(
        f"  {pdf.name:<36} {m.get('title_zh', '')}  {m.get('title_en', '')}" for pdf, m in entries)
    heading = f"{title} stories — Chinese / English facing-page readers ({a.version})"
    readme = README.format(heading=heading, rule="=" * len(heading),
                           count=len(entries), listing=listing, repo=a.repo)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    name = f"{a.level}-stories-{a.version}"
    zpath = out / f"{name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{name}/README.txt", readme.replace("\n", "\r\n"))
        z.write(ROOT / "LICENSE-TEXTS", f"{name}/LICENSE-TEXTS.txt")
        for pdf, _ in entries:
            z.write(pdf, f"{name}/{pdf.name}")
    print(f"{zpath}  ({len(entries)} PDFs, {zpath.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
