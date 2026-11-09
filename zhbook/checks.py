"""Validation of annotated records (see SCHEMA.md)."""
from __future__ import annotations

from dataclasses import dataclass

from .common import (Record, Token, cedict, count_hanzi, decode_syllable,
                     hsk_level, is_hanzi, split_pinyin, tone_mark_ok)

VALID_TYPES = {"meta", "h1", "h2", "p"}
VALID_KINDS = {"", "N", "J", "I"}


@dataclass
class Issue:
    level: str      # 'ERROR' or 'WARN' or 'INFO'
    rec: str
    msg: str

    def __str__(self) -> str:
        return f"{self.level:5s} [{self.rec}] {self.msg}"


def _diff(got: str, want: str) -> str:
    i = next((k for k, (x, y) in enumerate(zip(got, want)) if x != y), min(len(got), len(want)))
    return f"at char {i}: tokens …{got[max(0, i-6):i+6]}… vs source …{want[max(0, i-6):i+6]}…"


def _numbered(sylls: list[str]) -> list[tuple[str, int]]:
    return [decode_syllable(s)[:2] for s in sylls]


def check_token(t: Token, rid: str, use_cedict: bool) -> list[Issue]:
    out: list[Issue] = []
    if not t.w:
        return [Issue("ERROR", rid, "empty token")]
    if t.k not in VALID_KINDS:
        out.append(Issue("WARN", rid, f"{t.w}: unknown kind {t.k!r}"))
    n = count_hanzi(t.w)
    if n == 0:
        if t.py:
            out.append(Issue("WARN", rid, f"{t.w!r}: pinyin given for a token without hanzi"))
        return out
    if not t.py:
        return [Issue("ERROR", rid, f"{t.w}: missing pinyin")]
    if n != len(t.w):
        out.append(Issue("INFO", rid, f"{t.w}: mixed hanzi/other characters, syllable check skipped"))
        return out
    splits = split_pinyin(t.py)
    if splits is None:
        return out                                  # no syllable inventory available
    good = [s for s in splits if len(s) == n]
    if not good:
        got = len(splits[0]) if splits else 0
        why = "not parseable as pinyin" if not splits else f"{got} syllables for {n} characters"
        return out + [Issue("ERROR", rid, f"{t.w} {t.py}: {why}")]
    sylls = good[0]
    for s in sylls:
        if decode_syllable(s)[2] > 1:
            out.append(Issue("ERROR", rid, f"{t.w} {t.py}: several tone marks in '{s}'"))
        elif not tone_mark_ok(s):
            out.append(Issue("WARN", rid, f"{t.w} {t.py}: tone mark misplaced in '{s}'"))
    if use_cedict and cedict():
        mine = [(b.replace("ü", "u:"), tn or 5) for b, tn in _numbered(sylls)]
        entries = cedict().get(t.w)
        if entries:
            cands = []
            for py, _ in entries:
                parts = py.lower().split()
                cands.append([(p[:-1], int(p[-1])) if p[-1:].isdigit() else (p, 5) for p in parts])
            if mine not in cands:
                # same syllables, differing only in neutral tone -> INFO, else WARN
                soft = any(len(c) == len(mine) and all(a[0] == b[0] and (a[1] == b[1] or 5 in (a[1], b[1]))
                                                        for a, b in zip(c, mine)) for c in cands)
                alts = " / ".join(sorted({p for p, _ in entries}))
                out.append(Issue("INFO" if soft else "WARN", rid,
                                 f"{t.w} {t.py}: CC-CEDICT has [{alts}]"))
        else:
            for ch, (b, tn) in zip(t.w, mine):
                ce = cedict().get(ch)
                if not ce:
                    continue
                readings = {p.lower()[:-1] for py, _ in ce for p in py.split() if p[-1:].isdigit()}
                if b not in readings and not (ch == "儿" and b == "r"):
                    out.append(Issue("WARN", rid, f"{t.w} {t.py}: '{ch}' read '{b}', CC-CEDICT knows {sorted(readings)}"))
    return out


def check_records(recs: list[Record], source: dict[str, str] | None = None,
                  threshold: int | None = None, use_cedict: bool = True) -> list[Issue]:
    issues: list[Issue] = []
    seen: set[str] = set()
    for r in recs:
        rid = r.id
        if r.type not in VALID_TYPES:
            issues.append(Issue("ERROR", rid, f"unknown type {r.type!r}"))
            continue
        if rid in seen:
            issues.append(Issue("ERROR", rid, "duplicate id"))
        seen.add(rid)
        if r.type == "meta":
            continue
        if not r.segs:
            issues.append(Issue("ERROR", rid, "no segs"))
            continue
        joined = r.zh_from_tokens
        if r.zh and joined != r.zh:
            issues.append(Issue("ERROR", rid, "tokens do not reproduce 'zh': " + _diff(joined, r.zh)))
        if source is not None:
            src = source.get(rid)
            if src is None:
                issues.append(Issue("WARN", rid, "id not in source file"))
            elif src != joined:
                issues.append(Issue("ERROR", rid, "tokens differ from the source text: " + _diff(joined, src)))
        for k, s in enumerate(r.segs):
            if not s.en.strip():
                issues.append(Issue("ERROR", rid, f"seg {k}: empty English"))
            if not s.tok:
                issues.append(Issue("ERROR", rid, f"seg {k}: no tokens"))
            for t in s.tok:
                issues += check_token(t, rid, use_cedict)
                if threshold is not None and t.has_hanzi and not t.gl and t.k != "N":
                    lv, _ = hsk_level(t.w)
                    if (lv is None or lv > threshold or t.k) and not cedict().get(t.w):
                        issues.append(Issue("WARN", rid, f"{t.w}: would be annotated but has no gloss "
                                                         f"(and none in CC-CEDICT)"))
    if source is not None:
        for sid in source:
            if sid not in seen:
                issues.append(Issue("ERROR", sid, "source paragraph missing from annotations"))
    return issues
