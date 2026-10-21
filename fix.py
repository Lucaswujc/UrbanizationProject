#!/usr/bin/env python3
"""
Fix notebooks that GitHub refuses to render with:
    Invalid Notebook: the 'state' key is missing from 'metadata.widgets'

Keeps the widget metadata but adds an empty "state" object where it's missing.

Usage:
    python fix_widget_state.py                  # fix all .ipynb files under the current folder
    python fix_widget_state.py a.ipynb b.ipynb  # fix specific notebooks
"""

import json
import sys
from pathlib import Path

WIDGET_KEY = "application/vnd.jupyter.widget-state+json"


def fix_notebook(path: Path) -> bool:
    """Add an empty widget state if missing. Returns True if the file was changed."""
    try:
        with path.open(encoding="utf-8") as f:
            nb = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"  skipped (not valid JSON): {path} ({e})")
        return False

    widgets = nb.get("metadata", {}).get("widgets")
    if not isinstance(widgets, dict):
        return False  # no widget metadata, nothing to fix

    changed = False

    # Some tools save widget metadata without the MIME-type wrapper.
    if WIDGET_KEY not in widgets:
        widgets[WIDGET_KEY] = {}
        changed = True

    entry = widgets[WIDGET_KEY]
    if not isinstance(entry, dict):
        entry = widgets[WIDGET_KEY] = {}
        changed = True

    if "state" not in entry:
        entry["state"] = {}
        changed = True
    if "version_major" not in entry:
        entry["version_major"] = 2
        changed = True
    if "version_minor" not in entry:
        entry["version_minor"] = 0
        changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return changed


def main() -> None:
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        paths = [
            p for p in Path(".").rglob("*.ipynb") if ".ipynb_checkpoints" not in p.parts
        ]

    if not paths:
        print("No notebooks found.")
        return

    fixed = 0
    for path in paths:
        if not path.is_file():
            print(f"  not found: {path}")
            continue
        if fix_notebook(path):
            print(f"  fixed: {path}")
            fixed += 1

    print(f"Done. {fixed} of {len(paths)} notebook(s) updated.")


if __name__ == "__main__":
    main()
 