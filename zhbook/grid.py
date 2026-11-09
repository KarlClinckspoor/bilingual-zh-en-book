"""Chinese fixed-grid line breaking.

Every full-width character (hanzi and CJK punctuation alike) occupies exactly
one cell. Runs of half-width characters (Latin letters, digits) are packed two
per cell, as on Chinese manuscript paper. Line-breaking rules (kinsoku):

* a row may not start with closing punctuation (，。、；：？！）」』”’》)
* a row may not end with opening punctuation (（「『“‘《)
* ——/…… pairs are never split (they may start a row)

When a closing mark would start a row it is hung in the margin (one cell past
the last column) if possible; otherwise the preceding character is pushed down
to the next row, leaving an empty cell. Nothing is ever compressed.
"""
from __future__ import annotations

from dataclasses import dataclass

NO_START = set("，。、；：？！）］｝〕〉》」』】〗〙〟”’～·%‰℃,.;:?!)]}") | {"・"}
NO_END = set("（［｛〔〈《「『【〖〘〝“‘([{")
HANGABLE = set("，。、；：？！”’）》」』,.;:?!")
OPEN_ALIGN_RIGHT = set("“‘")
CLOSE_ALIGN_LEFT = set("”’")
PAIRS = {"—", "…"}
MAX_SPAN_RUN = 8     # half-width runs up to this length are kept unbroken and centred


@dataclass
class Unit:
    text: str        # 1 full-width char, or a run of half-width chars
    tok: int         # index into the flat token list of the block
    align: str       # 'c', 'l', 'r'
    span: int = 1    # cells covered (half-width runs are centred over ceil(n/2) cells)
    cont: bool = False  # placeholder cell covered by the preceding spanning unit

    @property
    def first(self) -> str:
        return self.text[0]

    @property
    def last(self) -> str:
        return self.text[-1]


def _is_halfwidth(ch: str) -> bool:
    return ord(ch) < 0x2000 and ch not in "—…"


def units_from_tokens(words: list[str]) -> list[Unit]:
    units: list[Unit] = []
    for ti, w in enumerate(words):
        i = 0
        while i < len(w):
            ch = w[i]
            if _is_halfwidth(ch):
                j = i
                while j < len(w) and _is_halfwidth(w[j]):
                    j += 1
                run = w[i:j]
                if len(run) <= MAX_SPAN_RUN:
                    # short runs (3D, CAD, 2016, uncle) are centred over the cells
                    # they need, so odd lengths do not leave a lone character
                    span = (len(run) + 1) // 2
                    units.append(Unit(run, ti, "c", span=span))
                    units += [Unit("", ti, "c", cont=True) for _ in range(span - 1)]
                else:
                    for k in range(0, len(run), 2):
                        units.append(Unit(run[k:k + 2], ti, "c"))
                i = j
                continue
            align = "r" if ch in OPEN_ALIGN_RIGHT else "l" if ch in CLOSE_ALIGN_LEFT else "c"
            units.append(Unit(ch, ti, align))
            i += 1
    return units


def break_rows(units: list[Unit], cols: int, indent: int = 0, hang: bool = True,
               keep_words: bool = False, word_has_hanzi=None) -> list[list[tuple[Unit, int]]]:
    """Distribute units over rows. Returns rows of (unit, column)."""

    def legal(j: int, strict_words: bool) -> bool:
        # may we break between units[j-1] and units[j]?
        if j <= 0 or j >= len(units):
            return True
        a, b = units[j - 1], units[j]
        if b.cont:
            return False
        if b.text and b.first in NO_START or a.text and a.last in NO_END:
            return False
        if a.text and b.text and a.last in PAIRS and b.first == a.last:
            return False
        if strict_words and a.tok == b.tok and (word_has_hanzi is None or word_has_hanzi(a.tok)):
            return False
        return True

    rows: list[list[tuple[Unit, int]]] = []
    i, first = 0, True
    while i < len(units):
        start = indent if first else 0
        cap = cols - start
        n = min(cap, len(units) - i)
        if i + n < len(units) and not legal(i + n, keep_words):
            done = False
            if hang and units[i + n].text in HANGABLE and legal(i + n + 1, False):
                n += 1                                  # hang one mark in the margin
                done = True
            if not done:
                for strict in ([True, False] if keep_words else [False]):
                    m = next((m for m in range(n - 1, 0, -1) if legal(i + m, strict)), None)
                    if m is not None:
                        n = m
                        break
        rows.append([(units[i + k], start + k) for k in range(n)])
        i += n
        first = False
    return rows
