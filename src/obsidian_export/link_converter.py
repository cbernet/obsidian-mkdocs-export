import re
from pathlib import PurePosixPath
from urllib.parse import quote


def _find_known_path(filename: str, known_files: set[str]) -> str | None:
    """Find the full relative path for a filename in known_files."""
    for path in known_files:
        if path.endswith("/" + filename) or path == filename:
            return path
    return None


def _make_relative(target_path: str, current_file: str) -> str:
    """Make target_path relative to the directory containing current_file."""
    current_dir = PurePosixPath(current_file).parent
    target = PurePosixPath(target_path)
    try:
        rel = target.relative_to(current_dir)
        return str(rel)
    except ValueError:
        # Need to go up with ../
        ups = len(current_dir.parts)
        return str(PurePosixPath(*[".."] * ups) / target)


def _replace_wiki_link(match: re.Match, known_files: set[str], current_file: str) -> str:
    is_embed = match.group(1) == "!"
    inner = match.group(2)

    # Anchor link: [[#heading]]
    if inner.startswith("#"):
        heading = inner[1:]
        slug = heading.lower().replace(" ", "-")
        return f"[{heading}](#{slug})"

    # Image/file embed: ![[path]]
    if is_embed:
        filename = inner.split("/")[-1]
        known_path = _find_known_path(filename, known_files)
        if known_path:
            rel = _make_relative(known_path, current_file)
            return f"![]({quote(rel, safe='/.:')})"
        return f"![]({quote(inner, safe='/.:')})"

    # Link with alias: [[path|alias]]
    if "|" in inner:
        target, alias = inner.split("|", 1)
        filename = target.split("/")[-1]
        if not filename.endswith(".md"):
            filename += ".md"
        known_path = _find_known_path(filename, known_files)
        if known_path:
            rel = _make_relative(known_path, current_file)
            return f"[{alias}]({quote(rel, safe='/.:')})"
        return f"**{alias}**"

    # Simple link: [[Note Name]]
    filename = inner.split("/")[-1]
    if not filename.endswith(".md"):
        filename += ".md"
    known_path = _find_known_path(filename, known_files)
    if known_path:
        rel = _make_relative(known_path, current_file)
        return f"[{inner.split('/')[-1]}]({quote(rel, safe='/.:')})"
    return f"**{inner}**"


WIKI_LINK_PATTERN = r"(!?)\[\[([^\]]+)\]\]"


def convert_wiki_links(content: str, known_files: set[str], current_file: str) -> str:
    return re.sub(WIKI_LINK_PATTERN, lambda m: _replace_wiki_link(m, known_files, current_file), content)
