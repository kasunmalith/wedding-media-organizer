"""Regenerate the readable single-file revision from the maintained modules."""
from pathlib import Path
import ast

root = Path(__file__).resolve().parent
target = root.parent / 'WeddingMediaOrganizer.py'
parts = ['''"""Wedding Media File Organizer 1.0.3 — Python revision, no installer.

Requires Python 3.12+ and PySide6. Run this file or the accompanying launcher.
Generated from the supplied maintained source modules by make_single_file.py.
"""
from __future__ import annotations
''']
for name in ('branding', 'model', 'safety', 'planner', 'engine', 'gui'):
    source = (root / 'wedding_organizer' / f'{name}.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    removed = set()
    for statement in tree.body:
        if isinstance(statement, ast.ImportFrom) and (statement.level or statement.module == '__future__'):
            removed.update(range(statement.lineno, statement.end_lineno + 1))
    parts.append(f'\n# ==================== {name.upper()} ====================\n' +
                 '\n'.join(line for number, line in enumerate(source.splitlines(), 1) if number not in removed) + '\n')
parts.append('\nif __name__ == "__main__":\n    raise SystemExit(main())\n')
target.write_text('\n'.join(parts), encoding='utf-8')
compile(target.read_text(encoding='utf-8'), str(target), 'exec')
print(target)
