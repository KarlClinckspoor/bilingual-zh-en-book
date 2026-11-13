#!/usr/bin/env python3
"""Small desktop front-end for the PDF build (standard library only: tkinter).

  python zhbook_gui.py

Pick stories from stories/ (or add any .jsonl / .zhb), set paper, fonts, HSK
note level and the other make_book.py options, then build. Each build runs
make_book.py in a subprocess, so the result is identical to the command line;
the equivalent command is printed in the log and can be copied.

Settings are remembered in ~/.zhbook-gui.json.
"""
from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

SETTINGS_FILE = Path.home() / ".zhbook-gui.json"
WIN = sys.platform == "win32"
# Frozen by PyInstaller (see build_exe.py): there is no separate Python, so the exe runs the
# project's scripts itself ("zhbook-gui.exe --run-script make_book.py ..."), and the project
# folder is found next to / above the exe or chosen once and remembered.
FROZEN = getattr(sys, "frozen", False)
PY = [sys.executable, "--run-script"] if FROZEN else [sys.executable]
PAPERS: dict = {"a5": {}, "a4": {}}
Config = None


def is_project(p: Path) -> bool:
    return (p / "make_book.py").is_file() and (p / "zhbook").is_dir()


def find_root() -> Path | None:
    if not FROZEN:
        return Path(__file__).resolve().parent
    start = Path(sys.executable).resolve().parent
    for p in (start, *start.parents, Path.cwd()):
        if is_project(p):
            return p
    try:
        saved = Path(json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))["project_dir"])
        return saved if is_project(saved) else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def set_root(p: Path) -> None:
    global ROOT, PAPERS, Config
    ROOT = p.resolve()
    sys.path.insert(0, str(ROOT))
    try:
        from zhbook.book import PAPERS, Config
    except Exception:  # the GUI still runs; only the geometry preview is lost
        pass


ROOT = find_root() or Path.cwd()
if not FROZEN:
    set_root(ROOT)

DEFAULTS = dict(
    paper="a5", cell="", en_size="", en_lead="", lines_per_row="2",
    m_top="", m_bottom="", m_inner="", m_outer="",
    para_gap="1", gridlines="none", note_cols="2",
    hang=True, keep_words=False, para_numbers=True,
    underline="all", annotate_above="4", kind_N=True, kind_J=True, kind_I=True,
    scope="page", marks="auto",
    zh_font="Noto Serif CJK SC", zh_head_font="Noto Serif CJK SC Bold", en_font="TeX Gyre Pagella",
    out_dir="work/pdfs", combine=False, combined_name="book", keep_build=False, replace_repo=False,
    regen_zhb=True, force=False, tex_only=False, open_after=True,
)
ANNOTATE_LEVELS = ["none", "1", "2", "3", "4", "5", "6", "7 (band 7-9)"]
# Fonts known to be free to embed and redistribute; anything else gets a licence reminder.
FREE_FONT = re.compile(r"^(Noto (Serif|Sans) CJK|Source Han|Fandol|TeX Gyre|Latin Modern|LXGW|"
                       r"Libertinus|Linux Libertine|EB Garamond|Noto Serif$|Noto Sans$)", re.I)
VARIABLE_TRAP = {"Noto Serif SC", "Noto Sans SC"}


@dataclass
class Source:
    jsonl: Path
    zhb: Path | None
    slug: str
    level: str          # "4", "5", ... or "" for files outside stories/
    title: str

    @property
    def in_stories(self) -> bool:
        return (ROOT / "stories") in self.jsonl.parents


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def read_meta(jsonl: Path) -> dict:
    try:
        with jsonl.open(encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("type") == "meta":
                    return rec
                break
    except (OSError, ValueError):
        pass
    return {}


def make_source(path: Path) -> Source:
    path = path.resolve()
    jsonl = path.with_suffix(".jsonl")
    zhb = path.with_suffix(".zhb")
    m = re.search(r"hsk(\d)", str(path.parent.parent.name)) if (ROOT / "stories") in path.parents else None
    meta = read_meta(jsonl)
    title = " · ".join(x for x in (meta.get("title_zh"), meta.get("title_en")) if x) or path.stem
    return Source(jsonl, zhb if zhb.exists() else None, path.stem, m.group(1) if m else "", title)


def discover() -> dict[str, list[Source]]:
    groups: dict[str, list[Source]] = {}
    for lvl in sorted((ROOT / "stories").glob("hsk*")):
        items = [make_source(j) for j in sorted(lvl.glob("*/*.jsonl"))]
        if items:
            groups[f"HSK {lvl.name[3:]}"] = items
    ex = [make_source(j) for j in sorted((ROOT / "examples").glob("*/*.jsonl"))]
    if ex:
        groups["Examples"] = ex
    return groups


def list_fonts() -> tuple[list[str], list[str]]:
    """(Chinese families, all families) as XeLaTeX/fontconfig sees them."""
    exe = shutil.which("fc-list")

    def run(*args):
        if not exe:
            return []
        try:
            out = subprocess.run([exe, *args, "family"], capture_output=True, text=True, encoding="utf-8",
                                 errors="replace", timeout=60, creationflags=_NOWINDOW).stdout
        except (OSError, subprocess.SubprocessError):
            return []
        return sorted({ln.split(",")[0].strip() for ln in out.splitlines() if ln.strip()}, key=str.lower)

    return run(":lang=zh"), run(":")


_NOWINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("zhbook – PDF builder")
        self.geometry("1180x780")
        self.minsize(980, 640)
        self.v: dict[str, tk.Variable] = {}
        self.sources: dict[str, Source] = {}
        self.extra: list[Source] = []
        self.q: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self.proc: subprocess.Popen | None = None
        self.stop_flag = threading.Event()
        self.last_pdf: Path | None = None

        saved = {}
        try:
            saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        for k, d in DEFAULTS.items():
            val = saved.get(k, d)
            self.v[k] = tk.BooleanVar(value=bool(val)) if isinstance(d, bool) else tk.StringVar(value=str(val))
        for p in saved.get("extra_files", []):
            if Path(p).exists():
                self.extra.append(make_source(Path(p)))

        self._build_ui()
        self.refresh_tree()
        for var in self.v.values():
            var.trace_add("write", lambda *_: self.update_preview())
        self.update_preview()
        threading.Thread(target=self._load_fonts, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self._poll)

    # ---------------------------------------------------------------- UI
    def _build_ui(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Hint.TLabel", foreground="#666")
        style.configure("Warn.TLabel", foreground="#b35c00")

        panes = ttk.PanedWindow(self, orient="vertical")
        panes.pack(fill="both", expand=True, padx=8, pady=8)
        top = ttk.PanedWindow(panes, orient="horizontal")
        panes.add(top, weight=3)

        # --- left: sources
        left = ttk.LabelFrame(top, text="Texts to build", padding=6)
        top.add(left, weight=3)
        cols = ("level", "title")
        self.tree = ttk.Treeview(left, columns=cols, show="tree headings", selectmode="extended")
        self.tree.heading("#0", text="file")
        self.tree.heading("level", text="HSK")
        self.tree.heading("title", text="title")
        self.tree.column("#0", width=230)
        self.tree.column("level", width=45, anchor="center")
        self.tree.column("title", width=330)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, columnspan=5, sticky="nsew")
        sb.grid(row=0, column=5, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.update_preview())
        self.tree.bind("<Double-1>", self._open_existing_pdf)
        for i, (txt, cmd) in enumerate([("Add file…", self.add_files), ("Remove added", self.remove_extra),
                                         ("Select all", self.select_all), ("Rescan", self.refresh_tree)]):
            ttk.Button(left, text=txt, command=cmd).grid(row=1, column=i, sticky="w", pady=(6, 0), padx=(0, 4))
        self.sel_label = ttk.Label(left, style="Hint.TLabel")
        self.sel_label.grid(row=2, column=0, columnspan=6, sticky="w", pady=(4, 0))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(4, weight=1)

        # --- right: options
        nb = ttk.Notebook(top)
        top.add(nb, weight=2)
        self._page_tab(nb)
        self._aids_tab(nb)
        self._fonts_tab(nb)
        self._output_tab(nb)

        # --- bottom: actions + log
        bottom = ttk.Frame(panes)
        panes.add(bottom, weight=2)
        bar = ttk.Frame(bottom)
        bar.pack(fill="x")
        self.build_btn = ttk.Button(bar, text="Build PDF", command=self.build)
        self.build_btn.pack(side="left")
        self.stop_btn = ttk.Button(bar, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=4)
        ttk.Button(bar, text="Validate", command=lambda: self.run_tool("validate")).pack(side="left", padx=(12, 4))
        ttk.Button(bar, text="HSK report", command=lambda: self.run_tool("hsk")).pack(side="left")
        ttk.Button(bar, text="Copy command", command=self.copy_command).pack(side="left", padx=(12, 4))
        ttk.Button(bar, text="Open output folder", command=self.open_out).pack(side="left")
        ttk.Button(bar, text="Clear log", command=lambda: self.log.delete("1.0", "end")).pack(side="right")
        self.status = ttk.Label(bar, text="")
        self.status.pack(side="left", padx=12)
        self.progress = ttk.Progressbar(bar, mode="determinate", length=160)
        self.progress.pack(side="right", padx=8)
        self.log = ScrolledText(bottom, height=12, font=("Consolas", 9), wrap="word")
        self.log.pack(fill="both", expand=True, pady=(6, 0))
        self.log.tag_configure("cmd", foreground="#2255aa")
        self.log.tag_configure("err", foreground="#b00020")
        self.log.tag_configure("ok", foreground="#1a7f37")

    def _row(self, parent, r, label, widget, hint=None):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", pady=2, padx=(0, 8))
        widget.grid(row=r, column=1, sticky="w", pady=2)
        if hint is not None:
            hint.grid(row=r, column=2, sticky="w", padx=6)

    def _num(self, parent, key, width=7):
        return ttk.Spinbox(parent, textvariable=self.v[key], width=width, from_=0, to=99, increment=1)

    def _page_tab(self, nb):
        f = ttk.Frame(nb, padding=10)
        nb.add(f, text="Page")
        self.hints: dict[str, ttk.Label] = {}
        self._row(f, 0, "Paper size", ttk.Combobox(f, textvariable=self.v["paper"], values=sorted(PAPERS),
                                                    state="readonly", width=6))
        for r, (key, label) in enumerate([("cell", "Chinese cell (mm)"), ("en_size", "English size (pt)"),
                                          ("en_lead", "English leading (pt)")], start=1):
            self.hints[key] = ttk.Label(f, style="Hint.TLabel")
            self._row(f, r, label, ttk.Entry(f, textvariable=self.v[key], width=8), self.hints[key])
        self._row(f, 4, "English lines per row", self._num(f, "lines_per_row"))
        mf = ttk.Frame(f)
        for i, (key, lab) in enumerate([("m_top", "top"), ("m_bottom", "bottom"),
                                        ("m_inner", "inner"), ("m_outer", "outer")]):
            ttk.Label(mf, text=lab, style="Hint.TLabel").grid(row=0, column=i, padx=2)
            ttk.Entry(mf, textvariable=self.v[key], width=5).grid(row=1, column=i, padx=2)
        self.hints["margins"] = ttk.Label(f, style="Hint.TLabel")
        self._row(f, 5, "Margins (mm)", mf, self.hints["margins"])
        self._row(f, 6, "Rows between paragraphs", self._num(f, "para_gap"))
        self._row(f, 7, "Grid lines", ttk.Combobox(f, textvariable=self.v["gridlines"], values=["none", "box"],
                                                    state="readonly", width=6), ttk.Label(f, text="box = 稿纸 cells", style="Hint.TLabel"))
        self._row(f, 8, "Footnote columns", self._num(f, "note_cols"))
        ttk.Checkbutton(f, text="Hang closing punctuation in the margin", variable=self.v["hang"]).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(8, 2))
        ttk.Checkbutton(f, text="Never split a word across rows", variable=self.v["keep_words"]).grid(
            row=10, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Checkbutton(f, text="Paragraph numbers in the margin", variable=self.v["para_numbers"]).grid(
            row=11, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Label(f, text="Blank fields use the paper's default.", style="Hint.TLabel").grid(
            row=12, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.geom = ttk.Label(f, wraplength=360, justify="left")
        self.geom.grid(row=13, column=0, columnspan=3, sticky="w", pady=(4, 0))

    def _aids_tab(self, nb):
        f = ttk.Frame(nb, padding=10)
        nb.add(f, text="Reading aids")
        self._row(f, 0, "Footnote words above HSK", ttk.Combobox(
            f, textvariable=self.v["annotate_above"], values=ANNOTATE_LEVELS, state="readonly", width=12),
            ttk.Label(f, text="none = only names/terms/idioms", style="Hint.TLabel"))
        kf = ttk.Frame(f)
        for key, lab in [("kind_N", "N names"), ("kind_J", "J terms"), ("kind_I", "I idioms")]:
            ttk.Checkbutton(kf, text=lab, variable=self.v[key]).pack(side="left", padx=(0, 8))
        self._row(f, 1, "Always footnote kinds", kf)
        ttk.Label(f, text="(unless the word is in the HSK list at or below the level)", style="Hint.TLabel").grid(
            row=2, column=1, columnspan=2, sticky="w")
        self._row(f, 3, "Word underlines", ttk.Combobox(f, textvariable=self.v["underline"],
                                                         values=["all", "multi", "none"], state="readonly", width=8),
                  ttk.Label(f, text="multi = only multi-character words", style="Hint.TLabel"))
        self._row(f, 4, "Footnote scope", ttk.Combobox(f, textvariable=self.v["scope"], values=["page", "book"],
                                                        state="readonly", width=8),
                  ttk.Label(f, text="first use per page, or once per book", style="Hint.TLabel"))
        self._row(f, 5, "Note marks", ttk.Combobox(f, textvariable=self.v["marks"],
                                                    values=["auto", "symbols", "numbers"], state="readonly", width=8),
                  ttk.Label(f, text="auto = †‡§ when ≤ 6 notes on a page", style="Hint.TLabel"))

    def _fonts_tab(self, nb):
        f = ttk.Frame(nb, padding=10)
        nb.add(f, text="Fonts")
        self.font_boxes = {}
        for r, (key, lab) in enumerate([("zh_font", "Chinese text"), ("zh_head_font", "Chinese headings"),
                                        ("en_font", "English text")]):
            cb = ttk.Combobox(f, textvariable=self.v[key], width=32)
            self.font_boxes[key] = cb
            self._row(f, r, lab, cb)
        ttk.Button(f, text="Free defaults (Noto / Pagella)", command=self.default_fonts).grid(
            row=3, column=1, sticky="w", pady=(6, 0))
        self.font_status = ttk.Label(f, text="Reading installed fonts…", style="Hint.TLabel")
        self.font_status.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.font_warn = ttk.Label(f, style="Warn.TLabel", wraplength=380, justify="left")
        self.font_warn.grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Label(f, style="Hint.TLabel", wraplength=380, justify="left",
                  text="Names are what XeLaTeX sees (fc-list). For a bold heading face you can type a name "
                       "with its style, e.g. “Noto Serif CJK SC Bold”, or use a different family such as SimHei.").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def _output_tab(self, nb):
        f = ttk.Frame(nb, padding=10)
        nb.add(f, text="Output")
        of = ttk.Frame(f)
        ttk.Entry(of, textvariable=self.v["out_dir"], width=30).pack(side="left")
        ttk.Button(of, text="…", width=3, command=self.choose_out).pack(side="left", padx=4)
        self._row(f, 0, "Output folder", of)
        ttk.Label(f, text="PDFs are saved as <folder>/<story>.pdf", style="Hint.TLabel").grid(
            row=1, column=1, columnspan=2, sticky="w")
        ttk.Checkbutton(f, text="Combine the selection into one book named", variable=self.v["combine"]).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(10, 2))
        ttk.Entry(f, textvariable=self.v["combined_name"], width=16).grid(row=2, column=2, sticky="w")
        checks = [
            ("regen_zhb", "Regenerate .jsonl from .zhb when the .zhb is newer"),
            ("keep_build", "Keep the build folder (book.tex) under <folder>/_build"),
            ("tex_only", "Only write the .tex (no PDF)"),
            ("force", "Build even if validation finds errors"),
            ("open_after", "Open the PDF when a single build finishes"),
            ("replace_repo", "Also replace the story's PDF in the repository"),
        ]
        for r, (key, lab) in enumerate(checks, start=3):
            ttk.Checkbutton(f, text=lab, variable=self.v[key]).grid(row=r, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Label(f, style="Warn.TLabel", wraplength=380, justify="left",
                  text="Repository PDFs are published: replace them only with the free default fonts.").grid(
            row=3 + len(checks), column=0, columnspan=3, sticky="w", pady=(4, 0))
        ttk.Button(f, text="Reset all settings to defaults", command=self.reset).grid(
            row=4 + len(checks), column=0, columnspan=2, sticky="w", pady=(14, 0))

    # ---------------------------------------------------------------- sources
    def refresh_tree(self):
        sel = {self.sources[i].jsonl for i in self.tree.selection() if i in self.sources}
        self.tree.delete(*self.tree.get_children())
        self.sources.clear()
        groups = discover()
        if self.extra:
            groups["Added files"] = self.extra
        for g, items in groups.items():
            gid = self.tree.insert("", "end", text=g, open=True)
            for s in items:
                iid = self.tree.insert(gid, "end", text=s.slug, values=(s.level, s.title))
                self.sources[iid] = s
                if s.jsonl in sel:
                    self.tree.selection_add(iid)
        self.update_preview()

    def selected(self) -> list[Source]:
        out, seen = [], set()
        for iid in self.tree.selection():
            kids = self.tree.get_children(iid) or (iid,)   # a group row selects its whole group
            for k in kids:
                s = self.sources.get(k)
                if s and s.jsonl not in seen:
                    seen.add(s.jsonl)
                    out.append(s)
        return out

    def add_files(self):
        paths = filedialog.askopenfilenames(parent=self, initialdir=ROOT, title="Add texts",
                                            filetypes=[("zhbook texts", "*.jsonl *.zhb"), ("all files", "*.*")])
        known = {s.jsonl for s in self.sources.values()}
        for p in paths:
            s = make_source(Path(p))
            if s.jsonl not in known:
                self.extra.append(s)
                known.add(s.jsonl)
        self.refresh_tree()

    def remove_extra(self):
        drop = {s.jsonl for s in self.selected()}
        if not drop:
            messagebox.showinfo("Remove", "Select the added files to remove.", parent=self)
            return
        self.extra = [s for s in self.extra if s.jsonl not in drop]
        self.refresh_tree()

    def select_all(self):
        self.tree.selection_set([i for i in self.sources])

    def _open_existing_pdf(self, event):
        s = self.sources.get(self.tree.identify_row(event.y))
        if not s:
            return
        for cand in (self.out_dir() / f"{s.slug}.pdf", s.jsonl.with_suffix(".pdf")):
            if cand.exists():
                open_path(cand)
                return

    # ---------------------------------------------------------------- settings
    def opts(self) -> dict:
        return {k: v.get() for k, v in self.v.items()}

    def out_dir(self) -> Path:
        p = Path(self.v["out_dir"].get().strip() or DEFAULTS["out_dir"])
        return p if p.is_absolute() else ROOT / p

    def choose_out(self):
        d = filedialog.askdirectory(parent=self, initialdir=self.out_dir() if self.out_dir().exists() else ROOT)
        if d:
            self.v["out_dir"].set(rel(Path(d)))

    def default_fonts(self):
        for k in ("zh_font", "zh_head_font", "en_font"):
            self.v[k].set(DEFAULTS[k])

    def reset(self):
        if messagebox.askyesno("Reset", "Reset every option to its default?", parent=self):
            for k, d in DEFAULTS.items():
                self.v[k].set(d)

    def save_settings(self):
        data = self.opts()
        data["project_dir"] = str(ROOT)
        data["extra_files"] = [str(s.jsonl if s.jsonl.exists() else s.zhb) for s in self.extra]
        try:
            SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError:
            pass

    def _load_fonts(self):
        zh, allf = list_fonts()
        self.q.put(("fonts", (zh, allf)))

    def _set_fonts(self, zh, allf):
        extra = [DEFAULTS["zh_font"], DEFAULTS["zh_head_font"]]
        zh_list = sorted(set(zh) | set(extra), key=str.lower)
        self.font_boxes["zh_font"]["values"] = zh_list
        self.font_boxes["zh_head_font"]["values"] = zh_list
        self.font_boxes["en_font"]["values"] = allf or [DEFAULTS["en_font"]]
        self.font_status.config(text=f"{len(zh)} Chinese families, {len(allf)} in total found by fc-list."
                                if allf else "fc-list not found; type font names by hand.")

    # ---------------------------------------------------------------- preview
    def update_preview(self, *_):
        o = self.opts()
        n = len(self.selected()) if hasattr(self, "tree") else 0
        if hasattr(self, "sel_label"):
            self.sel_label.config(text=f"{n} selected · a level row takes the whole level · "
                                       f"double-click opens the PDF")
        d = PAPERS.get(o["paper"], {})
        for key in ("cell", "en_size", "en_lead"):
            self.hints[key].config(text=f"default {d.get(key, '?')}")
        self.hints["margins"].config(text="default " + " ".join(str(d.get(k, "?"))
                                                                for k in ("top", "bottom", "inner", "outer")))
        # geometry
        if Config is None:
            self.geom.config(text="(zhbook package not importable – no preview)")
        else:
            try:
                kw = self._config_kwargs(o)
                c = Config(**kw)
                self.geom.config(foreground="", text=(
                    f"{o['paper'].upper()} {c.w:g}×{c.h:g} mm · grid {c.cols} × {c.rows} cells of {c.cell:g} mm\n"
                    f"row pitch {c.P:.2f} mm · English {c.en_size:g}/{c.en_lead:g} pt · notes {c.note_size:g} pt"))
            except (SystemExit, ValueError, TypeError, ZeroDivisionError) as e:
                self.geom.config(foreground="#b00020", text=f"⚠ {e}")
        # fonts
        warn = []
        for key in ("zh_font", "zh_head_font", "en_font"):
            name = o[key].strip()
            if name in VARIABLE_TRAP:
                warn.append(f"“{name}” is a variable font: XeLaTeX embeds only the ExtraLight master. "
                            f"Use Noto Serif/Sans CJK SC instead.")
            elif name and not FREE_FONT.match(name):
                warn.append(f"“{name}”: check its licence before sharing PDFs that embed it.")
        self.font_warn.config(text="\n".join(dict.fromkeys(warn)))

    @staticmethod
    def _config_kwargs(o: dict) -> dict:
        kw = dict(paper=o["paper"], k=int(o["lines_per_row"]), para_gap=int(o["para_gap"]),
                  note_cols=int(o["note_cols"]))
        for key in ("cell", "en_size", "en_lead"):
            if o[key].strip():
                kw[key] = float(o[key])
        m = margins(o)
        if m:
            kw.update(top=m[0], bottom=m[1], inner=m[2], outer=m[3])
        return kw

    # ---------------------------------------------------------------- commands
    def jobs(self, o: dict, srcs: list[Source]) -> list[tuple[str, list[Source]]]:
        if o["combine"] and len(srcs) > 1:
            name = re.sub(r"[^\w.-]+", "-", o["combined_name"].strip()) or "book"
            return [(name, srcs)]
        return [(s.slug, [s]) for s in srcs]

    def make_book_cmd(self, o: dict, files: list[Path], build_dir: Path) -> list[str]:
        cmd = [*PY, "make_book.py", *[rel(f) for f in files], "-o", rel(build_dir),
               "--paper", o["paper"], "--lines-per-row", o["lines_per_row"], "--para-gap", o["para_gap"],
               "--gridlines", o["gridlines"], "--note-cols", o["note_cols"], "--underline", o["underline"],
               "--annotate-above", o["annotate_above"].split()[0],
               "--annotate-kinds", "".join(k for k in "NJI" if o[f"kind_{k}"]),
               "--scope", o["scope"], "--marks", o["marks"],
               "--zh-font", o["zh_font"].strip(), "--zh-head-font", o["zh_head_font"].strip(),
               "--en-font", o["en_font"].strip()]
        for key, flag in (("cell", "--cell"), ("en_size", "--en-size"), ("en_lead", "--en-lead")):
            if o[key].strip():
                cmd += [flag, o[key].strip()]
        m = margins(o)
        if m:
            cmd += ["--margins", *[f"{x:g}" for x in m]]
        if not o["hang"]:
            cmd.append("--no-hang")
        if o["keep_words"]:
            cmd.append("--keep-words")
        if not o["para_numbers"]:
            cmd.append("--no-para-numbers")
        if o["tex_only"]:
            cmd.append("--no-pdf")
        if o["force"]:
            cmd.append("--force")
        return cmd

    def check_opts(self, o: dict) -> str | None:
        try:
            self._config_kwargs(o)
            if Config is not None:
                Config(**self._config_kwargs(o))
        except (ValueError, TypeError):
            return "A number field contains something that isn't a number."
        except SystemExit as e:
            return str(e)
        if not all(o[k].strip() for k in ("zh_font", "zh_head_font", "en_font")):
            return "All three font names must be filled in."
        return None

    def copy_command(self):
        o, srcs = self.opts(), self.selected()
        if not srcs:
            messagebox.showinfo("Copy command", "Select at least one text first.", parent=self)
            return
        name, group = self.jobs(o, srcs)[0]
        cmd = self.make_book_cmd(o, [s.jsonl for s in group], self.out_dir() / "_build" / name)
        cmd = ["python", *cmd[len(PY):]]
        text = subprocess.list2cmdline(cmd) if WIN else " ".join(map(_shquote, cmd))
        self.clipboard_clear()
        self.clipboard_append(text)
        self.write(text + "\n", "cmd")
        self.status.config(text="command copied" + (" (first job only)" if len(self.jobs(o, srcs)) > 1 else ""))

    # ---------------------------------------------------------------- running
    def build(self):
        if self.busy():
            return
        o, srcs = self.opts(), self.selected()
        if not srcs:
            messagebox.showinfo("Build", "Select one or more texts on the left.", parent=self)
            return
        err = self.check_opts(o)
        if err:
            messagebox.showerror("Build", err, parent=self)
            return
        if o["replace_repo"]:
            repo = [s for s in srcs if s.in_stories]
            nonfree = [o[k] for k in ("zh_font", "zh_head_font", "en_font") if not FREE_FONT.match(o[k].strip())]
            if nonfree and not o["tex_only"]:
                messagebox.showerror("Build", "“Replace the story's PDF in the repository” is on, but these fonts "
                                     "are not known to be free to redistribute:\n\n  " + "\n  ".join(nonfree) +
                                     "\n\nSwitch to the free defaults or turn the option off.", parent=self)
                return
            if repo and not messagebox.askyesno(
                    "Replace repository PDFs", f"This overwrites {len(repo)} published PDF(s) under stories/. "
                    "Continue?", parent=self):
                return
        self.save_settings()
        o["_out"] = self.out_dir()   # resolved here: worker threads must not touch Tk variables
        self.start(self._build_worker, o, self.jobs(o, srcs))

    def run_tool(self, which: str):
        if self.busy():
            return
        srcs = self.selected()
        if not srcs:
            messagebox.showinfo("Check", "Select one or more texts on the left.", parent=self)
            return
        o = self.opts()
        self.start(self._tool_worker, o, which, srcs)

    def busy(self) -> bool:
        return self.worker is not None and self.worker.is_alive()

    def start(self, fn, *args):
        self.stop_flag.clear()
        self.build_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.worker = threading.Thread(target=self._wrap, args=(fn, *args), daemon=True)
        self.worker.start()

    def _wrap(self, fn, *args):
        try:
            fn(*args)
        except Exception as e:  # report instead of dying silently in the thread
            self.q.put(("log", (f"internal error: {e!r}\n", "err")))
        finally:
            self.q.put(("done", None))

    def stop(self):
        self.stop_flag.set()
        p = self.proc
        if p and p.poll() is None:
            if WIN:  # make_book.py spawns xelatex; kill the whole tree
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True,
                               creationflags=_NOWINDOW)
            else:
                p.terminate()

    def run_cmd(self, cmd: list[str]) -> int:
        """Run in ROOT, stream output to the log. Called from the worker thread."""
        shown = ["python", *cmd[len(PY):]] if cmd[:len(PY)] == PY else cmd
        self.q.put(("log", ("$ " + subprocess.list2cmdline(shown) + "\n", "cmd")))
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        try:
            self.proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         text=True, encoding="utf-8", errors="replace", env=env,
                                         creationflags=_NOWINDOW)
        except OSError as e:
            self.q.put(("log", (f"could not start: {e}\n", "err")))
            return -1
        for line in self.proc.stdout:
            self.q.put(("log", (line, "err" if re.match(r"(ERROR|xelatex failed|Traceback)", line) else None)))
        rc = self.proc.wait()
        self.proc = None
        return rc

    def _maybe_regen(self, o: dict, s: Source) -> bool:
        if not s.zhb:
            return True
        stale = not s.jsonl.exists() or (o["regen_zhb"] and s.zhb.stat().st_mtime > s.jsonl.stat().st_mtime)
        if not stale:
            return True
        return self.run_cmd([*PY, "zhb2jsonl.py", rel(s.zhb), "-o", rel(s.jsonl)]) == 0

    def _build_worker(self, o: dict, jobs: list):
        out = o["_out"]
        ok, failed, last = 0, [], None
        for n, (name, group) in enumerate(jobs, 1):
            if self.stop_flag.is_set():
                break
            self.q.put(("status", (f"building {n}/{len(jobs)}: {name}", (n - 1) / len(jobs))))
            if not all(self._maybe_regen(o, s) for s in group):
                failed.append(name)
                continue
            build_dir = out / "_build" / name
            build_dir.mkdir(parents=True, exist_ok=True)
            if self.run_cmd(self.make_book_cmd(o, [s.jsonl for s in group], build_dir)) != 0:
                failed.append(name)
                continue
            try:
                if o["tex_only"]:
                    self.q.put(("log", (f"tex written: {rel(build_dir / 'book.tex')}\n", "ok")))
                else:
                    pdf = out / f"{name}.pdf"
                    shutil.copy2(build_dir / "book.pdf", pdf)
                    self.q.put(("log", (f"saved {rel(pdf)}\n", "ok")))
                    last = pdf
                    if o["replace_repo"] and len(group) == 1 and group[0].in_stories:
                        dest = group[0].jsonl.with_suffix(".pdf")
                        shutil.copy2(pdf, dest)
                        self.q.put(("log", (f"replaced {rel(dest)}\n", "ok")))
                    if not o["keep_build"]:
                        shutil.rmtree(build_dir, ignore_errors=True)
                ok += 1
            except OSError as e:
                self.q.put(("log", (f"could not save {name}: {e} (is the PDF open in a viewer?)\n", "err")))
                failed.append(name)
        if not o["keep_build"] and not o["tex_only"]:
            try:
                (out / "_build").rmdir()   # only if empty
            except OSError:
                pass
        stopped = " (stopped)" if self.stop_flag.is_set() else ""
        msg = f"{ok} built, {len(failed)} failed{stopped}" + (f": {', '.join(failed)}" if failed else "")
        self.q.put(("log", (msg + "\n\n", "err" if failed else "ok")))
        self.q.put(("status", (msg, 1.0)))
        if last and o["open_after"] and len(jobs) == 1 and not failed:
            self.q.put(("open", last))

    def _tool_worker(self, o: dict, which: str, srcs: list[Source]):
        level = o["annotate_above"].split()[0]
        for s in srcs:
            if self.stop_flag.is_set() or not self._maybe_regen(o, s):
                break
            if which == "validate":
                cmd = [*PY, "validate.py", rel(s.jsonl), "-q"]
                if level.isdigit():
                    cmd += ["--annotate-above", level]
            else:
                target = s.level or (level if level.isdigit() else "4")
                cmd = [*PY, "hsk_report.py", rel(s.jsonl), "--target", target]
            self.run_cmd(cmd)
        self.q.put(("status", (("validation" if which == "validate" else "HSK report") + " finished", 1.0)))

    def _poll(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "log":
                    self.write(*data)
                elif kind == "status":
                    self.status.config(text=data[0])
                    self.progress["value"] = data[1] * 100
                elif kind == "done":
                    self.build_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                elif kind == "open":
                    open_path(data)
                elif kind == "fonts":
                    self._set_fonts(*data)
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def write(self, text: str, tag: str | None = None):
        self.log.insert("end", text, tag or ())
        self.log.see("end")

    def open_out(self):
        d = self.out_dir()
        d.mkdir(parents=True, exist_ok=True)
        open_path(d)

    def on_close(self):
        if self.busy():
            if not messagebox.askyesno("Quit", "A build is running. Stop it and quit?", parent=self):
                return
            self.stop()
        self.save_settings()
        self.destroy()


def margins(o: dict) -> list[float] | None:
    keys = ("m_top", "m_bottom", "m_inner", "m_outer")
    vals = [o[k].strip() for k in keys]
    if not any(vals):
        return None
    d = PAPERS.get(o["paper"], {})
    return [float(v) if v else float(d[k[2:]]) for v, k in zip(vals, keys)]


def _shquote(s: str) -> str:
    return s if re.fullmatch(r"[\w./:=+-]+", s) else "'" + s.replace("'", "'\\''") + "'"


def open_path(p: Path):
    try:
        if WIN:
            os.startfile(p)  # noqa: S606 - opens with the user's default viewer
        else:
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(p)])
    except OSError as e:
        messagebox.showerror("Open", str(e))


def run_script(argv: list[str]) -> None:
    """Frozen mode: act as the Python interpreter for one of the project's scripts."""
    import runpy
    if sys.stdout is None:  # windowed exe: fall back to the pipe handles the GUI passed us
        sys.stdout = open(1, "w", encoding="utf-8", errors="replace", closefd=False)
        sys.stderr = open(2, "w", encoding="utf-8", errors="replace", closefd=False)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if WIN:  # this process has no console, so stop xelatex & co. from opening one each
        orig = subprocess.Popen.__init__

        def quiet_init(self, *a, **kw):
            kw["creationflags"] = kw.get("creationflags", 0) | _NOWINDOW
            orig(self, *a, **kw)
        subprocess.Popen.__init__ = quiet_init
    script = Path(argv[0]).resolve()
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script), *argv[1:]]
    runpy.run_path(str(script), run_name="__main__")


def main() -> None:
    if FROZEN and len(sys.argv) > 2 and sys.argv[1] == "--run-script":
        run_script(sys.argv[2:])
        return
    root = find_root()
    if root is None:
        hidden = tk.Tk()
        hidden.withdraw()
        while root is None:
            d = filedialog.askdirectory(parent=hidden,
                                        title="Choose the zhbook project folder (the one with make_book.py)")
            if not d:
                return
            root = Path(d) if is_project(Path(d)) else None
            if root is None:
                messagebox.showerror("zhbook", f"{d} has no make_book.py / zhbook folder.", parent=hidden)
        hidden.destroy()
    set_root(root)
    App().mainloop()


if __name__ == "__main__":
    main()
