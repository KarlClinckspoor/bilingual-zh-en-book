#!/usr/bin/env python3
"""Build dist/zhbook-gui.exe (or the platform equivalent) from zhbook_gui.py with PyInstaller.

  python -m venv .venv
  .venv/Scripts/python -m pip install pyinstaller      (Linux/macOS: .venv/bin/python)
  .venv/Scripts/python build_exe.py

The exe is a front-end only: it still needs this project folder (stories/, data/, zhbook/,
make_book.py ...) and XeLaTeX. It finds the folder when it sits inside it (dist/ does) or
asks for it once. The project's scripts are not frozen into the exe; the exe runs them with
its embedded Python, so edits to zhbook/ or make_book.py take effect without a rebuild.
For that it must carry every standard-library module those scripts import, which this
script collects by scanning their imports.
"""
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def stdlib_imports() -> list[str]:
    mods = set()
    for f in [*ROOT.glob("*.py"), *ROOT.glob("zhbook/*.py")]:
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                mods.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                mods.add(node.module)
    return sorted(m for m in mods if m.split(".")[0] in sys.stdlib_module_names and m != "__future__")


def main() -> int:
    hidden = stdlib_imports()
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
           "--name", "zhbook-gui",
           "--distpath", str(ROOT / "dist"),
           "--workpath", str(ROOT / "work" / "pyinstaller"),
           "--specpath", str(ROOT / "work" / "pyinstaller"),
           "--exclude-module", "zhbook",       # always use the project's own copy
           *[a for m in hidden for a in ("--hidden-import", m)],
           str(ROOT / "zhbook_gui.py")]
    print("bundling stdlib modules:", " ".join(hidden))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
