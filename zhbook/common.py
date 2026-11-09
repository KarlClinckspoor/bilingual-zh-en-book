"""Shared helpers: record loading, pinyin parsing, dictionary/HSK lookup.

No hard-coded syllable tables: the set of legal pinyin syllables is derived
at runtime from CC-CEDICT, and tone marks are decoded via Unicode
normalisation.
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

HANZI_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0003134f]")

# Tone marks as combining characters (after NFD decomposition).
_TONE_COMBINING = {"̄": 1, "́": 2, "̌": 3, "̀": 4}
_UMLAUT = "̈"


def is_hanzi(ch: str) -> bool:
    return bool(HANZI_RE.match(ch))


def count_hanzi(s: str) -> int:
    return sum(1 for c in s if is_hanzi(c))


# ---------------------------------------------------------------- tokens
@dataclass
class Token:
    w: str                    # surface text, exactly as in the source
    py: str = ""              # word-level pinyin with tone marks
    gl: str = ""              # short English gloss
    k: str = ""               # kind: N=name, J=jargon/term, I=idiom ('' = normal)
    hsk: str = ""             # optional level supplied by annotator

    @property
    def has_hanzi(self) -> bool:
        return count_hanzi(self.w) > 0


def parse_token(t) -> Token:
    if isinstance(t, str):
        return Token(w=t)
    if isinstance(t, list):
        vals = list(t) + [""] * (4 - len(t))
        return Token(w=vals[0], py=vals[1] or "", gl=vals[2] or "", k=vals[3] or "")
    if isinstance(t, dict):
        return Token(w=t["w"], py=t.get("py", ""), gl=t.get("gl", ""),
                     k=t.get("k", ""), hsk=str(t.get("hsk", "")))
    raise ValueError(f"bad token: {t!r}")


@dataclass
class Seg:
    en: str
    tok: list[Token]

    @property
    def zh(self) -> str:
        return "".join(t.w for t in self.tok)


@dataclass
class Record:
    type: str                 # 'meta', 'h1', 'h2', 'p'
    id: str
    zh: str = ""
    segs: list[Seg] = field(default_factory=list)
    raw: dict = field(default_factory=dict)
    line: int = 0

    @property
    def zh_from_tokens(self) -> str:
        return "".join(s.zh for s in self.segs)

    @property
    def en(self) -> str:
        return " ".join(s.en.strip() for s in self.segs)


def load_records(paths) -> list[Record]:
    recs: list[Record] = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError as e:
                    raise SystemExit(f"{path}:{n}: invalid JSON: {e}")
                typ = d.get("type", "p")
                segs = [Seg(en=s.get("en", ""), tok=[parse_token(t) for t in s.get("tok", [])])
                        for s in d.get("segs", [])]
                recs.append(Record(type=typ, id=str(d.get("id", f"{Path(path).stem}:{n}")),
                                   zh=d.get("zh", ""), segs=segs, raw=d, line=n))
    return recs


# ---------------------------------------------------------------- pinyin
def decode_syllable(s: str) -> tuple[str, int, int]:
    """Return (toneless lowercase base with 'ü', tone 0-4, number of tone marks)."""
    d = unicodedata.normalize("NFD", s.lower())
    base, tone, marks = [], 0, 0
    for ch in d:
        if ch in _TONE_COMBINING:
            tone = _TONE_COMBINING[ch]
            marks += 1
        elif ch == _UMLAUT:
            if base and base[-1] == "u":
                base[-1] = "ü"
        else:
            base.append(ch)
    b = "".join(base).replace("v", "ü")
    return b, tone, marks


_SYLLABLES: set[str] | None = None


def syllable_set() -> set[str]:
    """Toneless syllables attested in CC-CEDICT (plus erhua 'r')."""
    global _SYLLABLES
    if _SYLLABLES is None:
        syl: set[str] = set()
        for word, entries in cedict().items():
            if not all(is_hanzi(c) for c in word):
                continue                      # skip Latin-letter entries
            for py, _ in entries:
                parts = py.split()
                if len(parts) != len(word):
                    continue
                for s in parts:
                    s = s.lower().replace("u:", "ü")
                    s = re.sub(r"[1-5]$", "", s)
                    if s.isalpha() and (re.search("[aeiouü]", s) or s in ("m", "n", "ng", "hm", "hng", "r")):
                        syl.add(s)
        _SYLLABLES = syl
    return _SYLLABLES


def split_pinyin(py: str) -> list[list[str]] | None:
    """All ways of splitting a word's pinyin into legal syllables.

    Apostrophes, spaces and hyphens are hard boundaries. Returns a list of
    candidate splits (each a list of original-case syllables), or None if the
    syllable inventory is unavailable.
    """
    sylls = syllable_set()
    if not sylls:
        return None
    chunks = [c for c in re.split(r"['’\s\-]+", py) if c]
    results = [[]]
    for chunk in chunks:
        bases = [decode_syllable(ch)[0] for ch in chunk]   # per-character base

        memo: dict[int, list[list[str]]] = {}

        def rec(i: int) -> list[list[str]]:
            if i == len(chunk):
                return [[]]
            if i in memo:
                return memo[i]
            out = []
            for j in range(min(len(chunk), i + 7), i, -1):   # longest first
                b = "".join(bases[i:j])
                # pinyin orthography: a syllable starting with a/o/e inside a
                # chunk must be preceded by an apostrophe, so reject such splits
                if b in sylls and not (i > 0 and b[0] in "aoe"):
                    for rest in rec(j):
                        out.append([chunk[i:j]] + rest)
            memo[i] = out[:20]
            return memo[i]

        opts = rec(0)
        if not opts:
            return []
        results = [r + o for r in results for o in opts][:50]
    return results


def tone_mark_ok(syl: str) -> bool:
    """Check the tone mark sits on the conventional vowel."""
    d = unicodedata.normalize("NFD", syl.lower())
    pos, letters = None, []
    for ch in d:
        if ch in _TONE_COMBINING:
            pos = len(letters) - 1
        elif ch != _UMLAUT:
            letters.append(ch)
    if pos is None:
        return True
    w = "".join(letters)
    if "a" in w:
        return w[pos] == "a"
    if "e" in w:
        return w[pos] == "e"
    if "ou" in w:
        return w[pos] == "o"
    vowels = [i for i, c in enumerate(w) if c in "aeiouv"]
    return bool(vowels) and pos == vowels[-1]


def pinyin_to_numbered(py: str) -> str:
    """'Zhōngqiūjié' -> 'zhong1 qiu1 jie2' using the first legal split."""
    splits = split_pinyin(py)
    if not splits:
        return ""
    out = []
    for s in splits[0]:
        b, t, _ = decode_syllable(s)
        out.append(f"{b.replace('ü', 'u:')}{t or 5}")
    return " ".join(out)


# ---------------------------------------------------------------- dictionaries
_CEDICT: dict | None = None


def cedict() -> dict[str, list[tuple[str, str]]]:
    """simplified -> [(numbered pinyin, '/def/def/'), ...]; empty if missing."""
    global _CEDICT
    if _CEDICT is None:
        _CEDICT = {}
        for name in ("cedict_ts.u8.gz", "cedict_ts.u8"):
            p = DATA / name
            if p.exists():
                op = gzip.open if name.endswith(".gz") else open
                pat = re.compile(r"^(\S+) (\S+) \[([^\]]*)\] /(.*)/\s*$")
                with op(p, "rt", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("#"):
                            continue
                        m = pat.match(line)
                        if m:
                            _CEDICT.setdefault(m.group(2), []).append((m.group(3), m.group(4)))
                break
    return _CEDICT


def cedict_gloss(word: str, numbered: str = "", maxlen: int = 60) -> str:
    entries = cedict().get(word, [])
    if not entries:
        return ""
    best = entries[0]
    if numbered:
        for e in entries:
            if e[0].lower() == numbered.lower():
                best = e
                break
    senses = [s for s in best[1].split("/") if s and not s.startswith(("variant of", "CL:", "old variant"))]
    out = ""
    for s in senses:
        cand = s if not out else out + "; " + s
        if len(cand) > maxlen and out:
            break
        out = cand
    return out


_HSK: tuple[dict, dict] | None = None


def _lvl(s: str) -> int:
    s = s.strip()
    return 7 if s.startswith("7") else int(s)


def hsk_tables() -> tuple[dict[str, int], dict[str, int]]:
    """(word -> level, char -> level) from the HSK 3.0 lists (7 = band 7-9)."""
    global _HSK
    if _HSK is None:
        words: dict[str, int] = {}
        chars: dict[str, int] = {}
        wp = DATA / "hsk30-expanded.csv"
        if wp.exists():
            with open(wp, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    lv = _lvl(row["Level"])
                    for w in row["Simplified"].split("|"):
                        w = w.strip()
                        if w and (w not in words or lv < words[w]):
                            words[w] = lv
        cp = DATA / "hsk30-chars.csv"
        if cp.exists():
            with open(cp, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    chars[row["Hanzi"]] = _lvl(row["Level"])
        _HSK = (words, chars)
    return _HSK


def hsk_level(word: str) -> tuple[int | None, str]:
    """Level of a word and how it was found: 'word', 'chars' or 'none'.

    Words not in the list fall back to the highest level among their
    characters (handles compositional tokens like 我们的). Returns
    (None, 'none') if any character is outside the list.
    """
    words, chars = hsk_tables()
    if word in words:
        return words[word], "word"
    hz = [c for c in word if is_hanzi(c)]
    if hz and all(c in chars for c in hz):
        return max(chars[c] for c in hz), "chars"
    return None, "none"
