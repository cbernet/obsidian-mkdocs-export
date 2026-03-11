from pathlib import Path

SKIP_DIRS = {"Assets"}
SUMMARY_MAX_CHARS = 500


def build_nav(docs_dir: Path, llm_order: bool = False) -> list:
    return _build_nav_for_dir(docs_dir, docs_dir, llm_order)


def _build_nav_for_dir(directory: Path, root: Path, llm_order: bool) -> list:
    items = []

    entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name))

    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            if entry.name in SKIP_DIRS:
                continue
            children = _build_nav_for_dir(entry, root, llm_order)
            if children:
                items.append({entry.name: children})
        elif entry.suffix == ".md":
            rel = str(entry.relative_to(root))
            title = entry.stem
            items.append({title: rel})

    if llm_order and items:
        items = _reorder_with_llm(items, directory)

    return items


def _reorder_with_llm(items: list[dict], directory: Path) -> list[dict]:
    from obsidian_export.llm_ordering import order_entries

    entries_for_llm = []
    for item in items:
        title = list(item.keys())[0]
        # For files, read a summary; for sections, just use the title
        value = item[title]
        if isinstance(value, str):
            path = directory / (title + ".md")
            # handle index.md or other names that differ from title
            if not path.exists():
                path = directory / value.split("/")[-1]
            summary = ""
            if path.exists():
                summary = path.read_text(encoding="utf-8")[:SUMMARY_MAX_CHARS]
            entries_for_llm.append({"title": title, "summary": summary})
        else:
            entries_for_llm.append({"title": title, "summary": f"Section: {title}"})

    ordered_titles = order_entries(entries_for_llm)

    items_by_title = {list(item.keys())[0]: item for item in items}
    ordered = []
    seen = set()
    for title in ordered_titles:
        if title in items_by_title and title not in seen:
            ordered.append(items_by_title[title])
            seen.add(title)
    # Append any entries the LLM missed, in alphabetical order
    for item in items:
        title = list(item.keys())[0]
        if title not in seen:
            ordered.append(item)
    return ordered
