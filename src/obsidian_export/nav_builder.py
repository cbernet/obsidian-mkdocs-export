from pathlib import Path

SKIP_DIRS = {"Assets"}


def build_nav(docs_dir: Path) -> list:
    return _build_nav_for_dir(docs_dir, docs_dir)


def _build_nav_for_dir(directory: Path, root: Path) -> list:
    items = []

    entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name))

    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            if entry.name in SKIP_DIRS:
                continue
            children = _build_nav_for_dir(entry, root)
            if children:
                items.append({entry.name: children})
        elif entry.suffix == ".md":
            rel = str(entry.relative_to(root))
            title = entry.stem
            items.append({title: rel})

    return items
