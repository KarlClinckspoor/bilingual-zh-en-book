#!/usr/bin/env python3
"""Download / refresh the dictionary data into ./data.

  python fetch_data.py

* HSK 3.0 word and character lists – github.com/ivankra/hsk30 (MIT)
* CC-CEDICT – mdbg.net (CC BY-SA 4.0); falls back to the copy bundled in the
  PyPI package 'pycccedict' if mdbg.net is unreachable.
"""
import io
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
HSK = "https://raw.githubusercontent.com/ivankra/hsk30/master/{}"
CEDICT = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "zhbook-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main() -> int:
    DATA.mkdir(exist_ok=True)
    for name in ("hsk30-expanded.csv", "hsk30-chars.csv"):
        try:
            (DATA / name).write_bytes(get(HSK.format(name)))
            print("ok  ", name)
        except Exception as e:
            print("FAIL", name, e, file=sys.stderr)
    try:
        (DATA / "cedict_ts.u8.gz").write_bytes(get(CEDICT))
        print("ok   cedict_ts.u8.gz (mdbg.net)")
    except Exception as e:
        print("mdbg.net unreachable:", e, "- trying PyPI pycccedict", file=sys.stderr)
        try:
            meta = json.loads(get("https://pypi.org/pypi/pycccedict/json"))
            url = next(f["url"] for f in meta["urls"] if f["filename"].endswith(".whl"))
            with zipfile.ZipFile(io.BytesIO(get(url))) as z:
                member = next(n for n in z.namelist() if n.endswith(".txt.gz"))
                with z.open(member) as src, open(DATA / "cedict_ts.u8.gz", "wb") as dst:
                    shutil.copyfileobj(src, dst)
            print("ok   cedict_ts.u8.gz (pycccedict)")
        except Exception as e2:
            print("FAIL cedict:", e2, file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
