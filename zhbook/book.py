"""Pagination and TeX generation for dual-language spreads.

Geometry model
--------------
* u  = English leading (baseline-to-baseline distance)
* P  = k * u  = Chinese row pitch (default k = 2: two English lines per row)
* each Chinese row = one square cell (side `cell`) + a gap (P - cell) that holds
  word underlines and note markers.
Everything is placed with absolute coordinates inside a picture environment,
so the Chinese grid never moves and paragraph pairs start on the same row on
the left (Chinese) and right (English) page.

English line counts and footnote line counts are measured by a quick XeLaTeX
pass first; Python then paginates with exact numbers.
"""
from __future__ import annotations

import math
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .common import (Record, Token, cedict_gloss, hsk_level, is_hanzi,
                     pinyin_to_numbered)
from .grid import Unit, break_rows, units_from_tokens

PT = 0.3514598  # mm per TeX point

PAPERS = {
    "a5": dict(w=148, h=210, top=17, bottom=18, inner=16, outer=12, en_size=10, en_lead=12, cell=5.6),
    "a4": dict(w=210, h=297, top=22, bottom=24, inner=22, outer=18, en_size=11, en_lead=13.5, cell=6.6),
}
SYMBOLS = ["†", "‡", "§", "¶", "*", "#"]
AUTO_MAX_SYMBOLS = 6


@dataclass
class Config:
    paper: str = "a5"
    w: float = 0
    h: float = 0
    top: float = 0
    bottom: float = 0
    inner: float = 0
    outer: float = 0
    en_size: float = 0
    en_lead: float = 0
    cell: float = 0
    k: int = 2                       # English lines per Chinese row
    zh_scale: float = 0.86           # glyph size / cell size
    note_size: float = 0             # pt, default en_size - 2.5
    para_gap: int = 1                # blank rows between paragraphs
    head_gap: int = 1                # extra blank rows before a heading
    underline: str = "all"           # all | multi | none
    annotate_above: int | None = 4   # HSK level; None = only by kind
    annotate_kinds: str = "NJI"
    scope: str = "page"              # page | book
    marks: str = "auto"              # auto | symbols | numbers
    gridlines: str = "none"          # none | box
    note_cols: int = 2               # footnote columns
    note_gap: float = 4.0            # mm between footnote columns
    para_numbers: bool = True
    keep_words: bool = False
    hang: bool = True
    zh_font: str = "Noto Serif CJK SC"
    zh_head_font: str = "Noto Serif CJK SC Bold"
    en_font: str = "TeX Gyre Pagella"

    def __post_init__(self):
        for key, val in PAPERS[self.paper].items():
            if not getattr(self, key):
                setattr(self, key, val)
        if not self.note_size:
            self.note_size = self.en_size - 2.5
        if self.cell >= self.P:
            raise SystemExit(f"cell ({self.cell} mm) must be smaller than the row pitch ({self.P:.2f} mm); "
                             f"increase --en-lead or --lines-per-row, or reduce --cell")

    # derived geometry (mm)
    @property
    def u(self) -> float: return self.en_lead * PT
    @property
    def P(self) -> float: return self.k * self.u
    @property
    def W(self) -> float: return self.w - self.inner - self.outer
    @property
    def H(self) -> float: return self.h - self.top - self.bottom
    @property
    def cols(self) -> int: return int((self.W + 1e-6) // self.cell)
    @property
    def rows(self) -> int: return int((self.H + 1e-6) // self.P)
    @property
    def x0(self) -> float: return (self.W - self.cols * self.cell) / 2
    @property
    def note_w(self) -> float: return (self.W - (self.note_cols - 1) * self.note_gap) / self.note_cols
    @property
    def f(self) -> float: return self.zh_scale * self.cell
    @property
    def zb(self) -> float:  # baseline offset of a Chinese glyph below the cell top
        return (self.cell - self.f) / 2 + 0.88 * self.f


# ---------------------------------------------------------------- TeX helpers
_TEX_SPECIAL = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&",
                "#": r"\#", "^": r"\^{}", "_": r"\_", "%": r"\%", "~": r"\textasciitilde{}"}
_CJK_RUN = re.compile(r"([⺀-〿㐀-鿿豈-﫿＀-￯\U00020000-\U0003134f]+)")


def esc(s: str) -> str:
    return "".join(_TEX_SPECIAL.get(c, c) for c in s)


def tex_text(s: str) -> str:
    """Escape running text; wrap CJK runs in the Chinese font."""
    parts = _CJK_RUN.split(s)
    return "".join(r"{\zhfont " + esc(p) + "}" if i % 2 else esc(p) for i, p in enumerate(parts))


def mm(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".")


def preamble(c: Config) -> str:
    return rf"""\documentclass[twoside]{{article}}
\usepackage[paperwidth={c.w}mm,paperheight={c.h}mm,top={c.top}mm,bottom={c.bottom}mm,inner={c.inner}mm,outer={c.outer}mm,headheight=12pt,headsep={mm(c.top*0.28)}mm,footskip={mm(c.bottom*0.5)}mm]{{geometry}}
\usepackage{{fontspec}}
\usepackage{{xcolor}}
\usepackage{{fancyhdr}}
\setmainfont{{{c.en_font}}}
\newfontfamily\zhfont{{{c.zh_font}}}
\newfontfamily\zhheadfont{{{c.zh_head_font}}}
\definecolor{{bbul}}{{gray}}{{0.45}}
\definecolor{{bbgrid}}{{gray}}{{0.78}}
\definecolor{{bbsoft}}{{gray}}{{0.5}}
\setlength\unitlength{{1mm}}
\setlength\topskip{{0pt}}
\setlength\parindent{{0pt}}
\newlength\bbW \setlength\bbW{{{mm(c.W)}mm}}
\newlength\bbmarkw \setlength\bbmarkw{{1.6em}}
\newcommand\bbzhsize{{\fontsize{{{mm(c.f)}mm}}{{{mm(c.f)}mm}}\selectfont}}
\newcommand\zc[1]{{\makebox[{mm(c.cell)}mm][c]{{#1}}}}
\newcommand\zl[1]{{\makebox[{mm(c.cell)}mm][l]{{#1}}}}
\newcommand\zr[1]{{\makebox[{mm(c.cell)}mm][r]{{#1}}}}
\newcommand\bbenfmt{{\fontsize{{{c.en_size}pt}}{{{c.en_lead}pt}}\selectfont\setlength\baselineskip{{{c.en_lead}pt}}%
  \lineskiplimit=-\maxdimen\parindent=1.2em\parfillskip=0pt plus 1fil\emergencystretch=2em\tolerance=1500}}
\newcommand\bbenpar[2]{{{{\bbenfmt\ifnum#1=1 \indent\else\noindent\fi #2\par\xdef\bbn{{\the\prevgraf}}}}}}
\newcommand\bbenhead[1]{{{{\bbenfmt\bfseries\centering #1\par\xdef\bbn{{\the\prevgraf}}}}}}
\newcommand\bbnotefmt{{\fontsize{{{c.note_size}pt}}{{{c.en_lead}pt}}\selectfont\setlength\baselineskip{{{c.en_lead}pt}}%
  \lineskiplimit=-\maxdimen\parfillskip=0pt plus 1fil\emergencystretch=2em\tolerance=2000\raggedright}}
\newcommand\bbnote[4]{{{{\bbnotefmt\noindent\hangindent=\bbmarkw\hangafter=1 \makebox[\bbmarkw][l]{{#1}}{{\zhfont #2}}\enspace{{\itshape #3}}\enspace #4\par\xdef\bbn{{\the\prevgraf}}}}}}
\newcommand\bbmark[1]{{{{\fontsize{{6pt}}{{6pt}}\selectfont #1}}}}
\newcommand\bbpnum[1]{{{{\fontsize{{6.5pt}}{{7pt}}\selectfont\color{{bbsoft}}#1}}}}
\newcommand\bbul[1]{{{{\color{{bbul}}\rule{{#1mm}}{{0.35pt}}}}}}
\newcommand\bbulN[1]{{{{\color{{bbul}}\rule{{#1mm}}{{0.3pt}}\llap{{\raisebox{{-0.45mm}}{{\rule{{#1mm}}{{0.3pt}}}}}}}}}}
\newcommand\bbzhhead{{}}\newcommand\bbenhd{{}}
\pagestyle{{fancy}}\fancyhf{{}}
\renewcommand\headrulewidth{{0pt}}
\fancyhead[LE]{{\footnotesize\color{{bbsoft}}{{\zhfont\bbzhhead}}}}
\fancyhead[RO]{{\footnotesize\itshape\color{{bbsoft}}\bbenhd}}
\fancyfoot[LE,RO]{{\footnotesize\thepage}}
"""


# ---------------------------------------------------------------- content model
@dataclass
class Block:
    rec: Record
    pno: int = 0                       # paragraph number (0 for headings)

    @property
    def kind(self) -> str: return self.rec.type
    @property
    def n(self) -> int: return len(self.rec.segs)

    def tokens(self, i: int, j: int) -> list[Token]:
        return [t for s in self.rec.segs[i:j] for t in s.tok]

    def en(self, i: int, j: int) -> str:
        return " ".join(s.en.strip() for s in self.rec.segs[i:j])


@dataclass
class Note:
    w: str
    py: str
    gl: str

    @property
    def key(self) -> tuple: return (self.w, self.py)


@dataclass
class Page:
    zh: list[str] = field(default_factory=list)
    en: list[str] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    keys: set = field(default_factory=set)
    row: int = 0
    heads: tuple = ("", "")


class BookBuilder:
    def __init__(self, recs: list[Record], cfg: Config, workdir: Path, log=print):
        self.c = cfg
        self.dir = workdir
        self.log = log
        self.meta = next((r.raw for r in recs if r.type == "meta"), {})
        self.blocks: list[Block] = []
        pno = 0
        for r in recs:
            if r.type == "meta":
                continue
            if r.type == "p":
                pno += 1
            self.blocks.append(Block(r, pno if r.type == "p" else 0))
        self.used_cedict = False
        self._rows_cache: dict = {}
        self.note_text: dict[tuple, Note] = {}
        self.warnings: list[str] = []

    # ------------------------------------------------ annotation policy
    def needs_note(self, t: Token) -> bool:
        if not t.has_hanzi:
            return False
        lv, how = hsk_level(t.w)
        thr = self.c.annotate_above
        if t.k and t.k in self.c.annotate_kinds:
            # names/terms/idioms are noted unless the word itself is in the HSK
            # list at or below the threshold (e.g. 春节 at a level-4 threshold)
            return thr is None or not (how == "word" and lv <= thr)
        if thr is None:
            return False
        return lv is None or lv > thr

    def note_for(self, t: Token) -> Note:
        key = (t.w, t.py)
        if key not in self.note_text:
            gl = t.gl
            if not gl:
                gl = cedict_gloss(t.w, pinyin_to_numbered(t.py))
                if gl:
                    self.used_cedict = True
                else:
                    self.warnings.append(f"no gloss for {t.w} {t.py}")
            self.note_text[key] = Note(t.w, t.py, gl)
        return self.note_text[key]

    # ------------------------------------------------ Chinese rows
    def zh_rows(self, b: Block, i: int, j: int):
        key = (id(b), i, j)
        if key not in self._rows_cache:
            toks = b.tokens(i, j)
            units = units_from_tokens([t.w for t in toks])
            if b.kind == "p":
                rows = break_rows(units, self.c.cols, indent=2 if i == 0 else 0, hang=self.c.hang,
                                  keep_words=self.c.keep_words, word_has_hanzi=lambda ti: toks[ti].has_hanzi)
            else:
                rows = break_rows(units, self.c.cols, hang=self.c.hang)
                if len(rows) == 1:                       # centre a one-row heading
                    off = (self.c.cols - len(rows[0])) // 2
                    rows = [[(u, col + off) for u, col in rows[0]]]
            self._rows_cache[key] = (toks, rows)
        return self._rows_cache[key]

    # ------------------------------------------------ measurement pass
    def measure(self) -> dict[str, int]:
        items = []
        for bi, b in enumerate(self.blocks):
            if b.kind == "p":
                for i in range(b.n):
                    for j in range(i + 1, b.n + 1):
                        items.append((f"e:{bi}:{i}:{j}", rf"\bbenpar{{{1 if i == 0 else 0}}}{{{tex_text(b.en(i, j))}}}", r"\bbW"))
            else:
                items.append((f"e:{bi}:0:{b.n}", rf"\bbenhead{{{tex_text(b.en(0, b.n))}}}", r"\bbW"))
            for t in b.tokens(0, b.n):
                if self.needs_note(t):
                    self.note_for(t)
        notes = list(self.note_text.values())
        for ni, n in enumerate(notes):
            items.append((f"n:{ni}", rf"\bbnote{{88}}{{{esc(n.w)}}}{{{tex_text(n.py)}}}{{{tex_text(n.gl)}}}",
                          f"{mm(self.c.note_w)}mm"))
        body = [preamble(self.c), r"\newwrite\bbout\immediate\openout\bbout=\jobname.mes", r"\begin{document}"]
        for key, tex, width in items:
            body.append(rf"\setbox0\vbox{{\hsize={width} {tex}}}\immediate\write\bbout{{{key} \bbn}}")
        body += [r"\immediate\closeout\bbout", r"\null", r"\end{document}"]
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "measure.tex").write_text("\n".join(body), encoding="utf-8")
        run_xelatex(self.dir, "measure.tex", nopdf=True)
        res: dict[str, int] = {}
        for line in (self.dir / "measure.mes").read_text(encoding="utf-8").splitlines():
            k, v = line.split()
            res[k] = int(v)
        self.note_lines = {notes[i].key: res[f"n:{i}"] for i in range(len(notes))}
        return res

    # ------------------------------------------------ pagination
    def reserve(self, note_lines: int) -> int:
        return math.ceil((note_lines + 1) / self.c.k) if note_lines else 0

    def note_columns(self, notes: list[Note]) -> tuple[int, list[list[Note]]]:
        """Split notes (in order) over the footnote columns, minimising height.

        Returns (height in lines, columns)."""
        if not notes:
            return 0, []
        lines = [self.note_lines[n.key] for n in notes]
        ncol = max(1, self.c.note_cols)

        def pack(h):
            cols, cur, used = [], [], 0
            for n, ln in zip(notes, lines):
                if cur and used + ln > h:
                    cols.append(cur)
                    cur, used = [], 0
                cur.append(n)
                used += ln
            cols.append(cur)
            return cols

        for h in range(max(lines), sum(lines) + 1):
            cols = pack(h)
            if len(cols) <= ncol:
                return max(sum(self.note_lines[n.key] for n in col) for col in cols), cols
        return sum(lines), [notes]

    def note_height(self, notes: list[Note]) -> int:
        return self.note_columns(notes)[0]

    def new_notes(self, page: Page, toks: list[Token], global_keys: set) -> list[Note]:
        out, seen = [], set()
        for t in toks:
            if self.needs_note(t):
                n = self.note_for(t)
                if n.key in page.keys or n.key in seen or (self.c.scope == "book" and n.key in global_keys):
                    continue
                seen.add(n.key)
                out.append(n)
        return out

    def fits(self, page: Page, start: int, b: Block, i: int, j: int, global_keys: set):
        toks, rows = self.zh_rows(b, i, j)
        en_lines = self.meas[f"e:{b.blocks_index}:{i}:{j}"]
        notes = self.new_notes(page, toks, global_keys)
        nl = self.note_height(page.notes + notes)
        R = self.c.rows
        ok = start + len(rows) <= R - self.reserve(nl) and start + math.ceil(en_lines / self.c.k) <= R
        height = max(len(rows), math.ceil(en_lines / self.c.k))
        return ok, height, notes

    def paginate(self) -> list[Page]:
        self.meas = self.measure()
        for bi, b in enumerate(self.blocks):
            b.blocks_index = bi
        c = self.c
        pages: list[Page] = []
        global_keys: set = set()
        heads = (self.meta.get("title_zh", ""), self.meta.get("title_en", ""))

        def new_page() -> Page:
            p = Page(heads=heads)
            pages.append(p)
            return p

        page = new_page()
        for bi, b in enumerate(self.blocks):
            if b.kind in ("h1", "h2"):
                heads = (b.rec.zh_from_tokens, b.en(0, b.n))
                if b.kind == "h1" and (page.row > 0):
                    page = new_page()
                gap = (c.para_gap + c.head_gap) if page.row > 0 else 0
                ok, height, notes = self.fits(page, page.row + gap, b, 0, b.n, global_keys)
                # keep with next: demand room for the heading plus 3 more rows
                if not ok or page.row + gap + height + c.para_gap + 3 > c.rows - self.reserve(self.note_height(page.notes)):
                    page = new_page()
                    gap = 0
                    ok, height, notes = self.fits(page, 0, b, 0, b.n, global_keys)
                if page.row == 0:
                    page.heads = heads
                self.commit(page, page.row + gap, b, 0, b.n, notes, global_keys, height)
                continue
            i = 0
            while i < b.n:
                gap = c.para_gap if page.row > 0 else 0
                best = None
                for j in range(b.n, i, -1):
                    ok, height, notes = self.fits(page, page.row + gap, b, i, j, global_keys)
                    if ok:
                        best = (j, height, notes)
                        break
                if best is None:
                    if page.row == 0:      # does not fit even on an empty page: force one segment
                        ok, height, notes = self.fits(page, 0, b, i, i + 1, global_keys)
                        self.warnings.append(f"{b.rec.id}: segment {i} is taller than a page; it will overflow")
                        best = (i + 1, height, notes)
                    else:
                        page = new_page()
                        continue
                j, height, notes = best
                self.commit(page, page.row + gap, b, i, j, notes, global_keys, height)
                i = j
                if i < b.n:
                    page = new_page()
        return pages

    # ------------------------------------------------ emission
    def commit(self, page: Page, start: int, b: Block, i: int, j: int, notes: list[Note],
               global_keys: set, height: int) -> None:
        c = self.c
        toks, rows = self.zh_rows(b, i, j)
        heading = b.kind != "p"
        # marks for new notes on this page
        note_tok_first: dict[tuple, int] = {}
        for n in notes:
            page.notes.append(n)
            page.keys.add(n.key)
            global_keys.add(n.key)
        new_keys = {n.key for n in notes}
        for ti, t in enumerate(toks):
            if (t.w, t.py) in new_keys and (t.w, t.py) not in note_tok_first:
                note_tok_first[(t.w, t.py)] = ti
        mark_of = {}
        for n in notes:
            idx = [x.key for x in page.notes].index(n.key)
            mark_of[note_tok_first[n.key]] = f"@@M{idx}@@"

        out = page.zh
        font = r"\zhheadfont" if heading else r"\zhfont"
        tok_cells: dict[int, list[tuple[int, int]]] = {}   # token -> [(row, col)]
        for r, row in enumerate(rows):
            ytop = (start + r) * c.P
            if c.gridlines == "box":
                out.append(self.grid_row(ytop))
            cells = []
            prev = 0
            for unit, col in row:
                tok_cells.setdefault(unit.tok, []).append((r, col))
                if unit.cont:                     # covered by the preceding spanning unit
                    prev = col + 1
                    continue
                while prev < col:
                    cells.append(r"\zc{}")
                    prev += 1
                if unit.span > 1:
                    cells.append(rf"\makebox[{mm(unit.span * c.cell)}mm][c]{{{esc(unit.text)}}}")
                else:
                    cmd = {"c": r"\zc", "l": r"\zl", "r": r"\zr"}[unit.align]
                    cells.append(f"{cmd}{{{esc(unit.text)}}}")
                prev = col + 1
            out.append(rf"\put({mm(c.x0)},{mm(-(ytop + c.zb))}){{\bbzhsize{font}{''.join(cells)}}}")
        # underlines and marks
        for ti, cl in tok_cells.items():
            t = toks[ti]
            draw = (c.underline == "all" or (c.underline == "multi" and len(t.w) > 1)) and t.has_hanzi and not heading
            if draw:
                byrow: dict[int, list[int]] = {}
                for r, col in cl:
                    byrow.setdefault(r, []).append(col)
                for r, cols_ in byrow.items():
                    x1 = c.x0 + min(cols_) * c.cell + 0.35
                    length = (max(cols_) - min(cols_) + 1) * c.cell - 0.7
                    y = (start + r) * c.P + c.cell + 0.55
                    macro = r"\bbulN" if t.k == "N" else r"\bbul"
                    out.append(rf"\put({mm(x1)},{mm(-y)}){{{macro}{{{mm(length)}}}}}")
            if ti in mark_of:
                r, col = cl[-1]
                x = c.x0 + (col + 1) * c.cell - 0.15 * c.cell
                y = (start + r) * c.P - 0.1
                out.append(rf"\put({mm(x)},{mm(-y)}){{\bbmark{{{mark_of[ti]}}}}}")
        # paragraph numbers (outer margins) and English text
        yb = start * c.P + c.zb
        if c.para_numbers and b.pno:
            out.append(rf"\put(-1.5,{mm(-yb)}){{\llap{{\bbpnum{{{b.pno}}}}}}}")
            page.en.append(rf"\put({mm(c.W + 1.5)},{mm(-yb)}){{\bbpnum{{{b.pno}}}}}")
        en = tex_text(b.en(i, j))
        body = rf"\bbenhead{{{en}}}" if heading else rf"\bbenpar{{{1 if i == 0 else 0}}}{{{en}}}"
        page.en.append(rf"\put(0,{mm(-yb)}){{\begin{{minipage}}[t]{{\bbW}}{body}\end{{minipage}}}}")
        page.row = start + height

    def grid_row(self, ytop: float) -> str:
        c = self.c
        n = c.cols
        return (rf"{{\color{{bbgrid}}\linethickness{{0.25pt}}"
                rf"\multiput({mm(c.x0)},{mm(-(ytop + c.cell))})({mm(c.cell)},0){{{n + 1}}}{{\line(0,1){{{mm(c.cell)}}}}}"
                rf"\put({mm(c.x0)},{mm(-ytop)}){{\line(1,0){{{mm(n * c.cell)}}}}}"
                rf"\put({mm(c.x0)},{mm(-(ytop + c.cell))}){{\line(1,0){{{mm(n * c.cell)}}}}}}}")

    def mark(self, idx: int, total: int) -> str:
        """Mark for the idx-th note of a page carrying `total` notes."""
        mode = self.c.marks
        if mode == "auto":
            mode = "symbols" if total <= AUTO_MAX_SYMBOLS else "numbers"
        if mode == "numbers":
            return str(idx + 1)
        n = len(SYMBOLS)
        return SYMBOLS[idx % n] * (idx // n + 1)       # †, ‡ … then ††, ‡‡ …

    def notes_tex(self, page: Page) -> str:
        if not page.notes:
            return ""
        c = self.c
        height, cols = self.note_columns(page.notes)
        y_last = c.rows * c.P - 0.25 * c.u         # baseline of the last note line
        y0 = y_last - (height - 1) * c.u           # baseline of the first note line
        y_rule = y0 - 0.95 * c.u
        total = len(page.notes)
        out = [rf"\put(0,{mm(-y_rule)}){{\color{{bbsoft}}\rule{{25mm}}{{0.3pt}}}}"]
        idx = 0
        for ci, col in enumerate(cols):
            body = ""
            for n in col:
                body += (rf"\bbnote{{{esc(self.mark(idx, total))}}}{{{esc(n.w)}}}"
                         rf"{{{tex_text(n.py)}}}{{{tex_text(n.gl)}}}")
                idx += 1
            x = ci * (c.note_w + c.note_gap)
            out.append(rf"\put({mm(x)},{mm(-y0)}){{\begin{{minipage}}[t]{{{mm(c.note_w)}mm}}{body}\end{{minipage}}}}")
        return "\n".join(out)

    # ------------------------------------------------ document
    def title_page(self) -> str:
        m = self.meta
        lines = [r"\thispagestyle{empty}", r"\begin{center}", r"\vspace*{30mm}"]
        if m.get("title_zh"):
            lines.append(rf"{{\zhheadfont\fontsize{{22pt}}{{30pt}}\selectfont {esc(m['title_zh'])}\par}}\vspace{{4mm}}")
        if m.get("subtitle_zh"):
            lines.append(rf"{{\zhfont\large {esc(m['subtitle_zh'])}\par}}\vspace{{10mm}}")
        if m.get("title_en"):
            lines.append(rf"{{\Large\bfseries {tex_text(m['title_en'])}\par}}\vspace{{3mm}}")
        if m.get("subtitle_en"):
            lines.append(rf"{{\itshape {tex_text(m['subtitle_en'])}\par}}")
        if m.get("author"):
            lines.append(rf"\vspace{{12mm}}{{\small {tex_text(m['author'])}\par}}")
        lines.append(r"\vfill")
        credits = []
        if m.get("note"):
            credits.append(tex_text(m["note"]))
        if self.c.annotate_above is not None:
            kinds = self.c.annotate_kinds
            if "N" in kinds and "J" in kinds:
                marked = "names, festival terms and "
            else:
                marked = "".join(f"{w} and " for k, w in (("N", "names"), ("J", "special terms"),
                                                           ("I", "idioms")) if k in kinds)
            credits.append(rf"Footnotes mark {marked}words above HSK~{self.c.annotate_above} "
                           r"(HSK 3.0 lists: github.com/ivankra/hsk30, MIT).")
        if self.used_cedict:
            credits.append(r"Some glosses from CC-CEDICT (MDBG), licensed CC BY-SA 4.0.")
        if credits:
            lines.append(r"{\footnotesize\color{bbsoft}" + r"\par ".join(credits) + r"\par}")
        lines += [r"\end{center}", r"\clearpage"]
        return "\n".join(lines)

    def build_tex(self) -> str:
        pages = self.paginate()
        out = [preamble(self.c), r"\begin{document}", self.title_page()]
        for p in pages:
            for side, content in (("zh", p.zh + [self.notes_tex(p)]), ("en", p.en)):
                zh_head, en_head = p.heads
                out.append(rf"\renewcommand\bbzhhead{{{esc(zh_head)}}}\renewcommand\bbenhd{{{tex_text(en_head)}}}")
                out.append(r"\noindent\begin{picture}(0,0)")
                total = len(p.notes)
                out += [re.sub(r"@@M(\d+)@@", lambda m: esc(self.mark(int(m.group(1)), total)), x)
                        for x in content if x]
                out.append(r"\end{picture}\par\null\clearpage")
        out.append(r"\end{document}")
        self.pages = pages
        return "\n".join(out)


def run_xelatex(d: Path, name: str, nopdf: bool = False) -> None:
    exe = shutil.which("xelatex")
    if not exe:
        raise SystemExit("xelatex not found on PATH (install TeX Live or MiKTeX)")
    cmd = [exe, "-interaction=nonstopmode", "-halt-on-error"] + (["-no-pdf"] if nopdf else []) + [name]
    r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        tail = "\n".join(r.stdout.splitlines()[-25:])
        raise SystemExit(f"xelatex failed on {d / name}:\n{tail}")
