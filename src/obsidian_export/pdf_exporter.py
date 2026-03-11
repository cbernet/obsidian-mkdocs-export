import os
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from obsidian_export.exporter import EXCLUDE, _collect_known_files, _copy_source
from obsidian_export.link_converter import WIKI_LINK_PATTERN, _find_known_path
from obsidian_export.nav_builder import build_nav

_CSS_FILE = Path(__file__).parent / "pdf_style.css"


def flatten_nav(nav: list) -> list[tuple[str, str]]:
    """Flatten nested nav tree into ordered list of (title, rel_path)."""
    result = []
    for item in nav:
        for key, value in item.items():
            if isinstance(value, list):
                result.extend(flatten_nav(value))
            else:
                result.append((key, value))
    return result


def slugify(title: str) -> str:
    """Convert a note title to an ASCII anchor slug."""
    import unicodedata
    # Normalize unicode and strip accents
    slug = unicodedata.normalize("NFKD", title)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = slug.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug


def strip_first_heading(content: str) -> str:
    """Remove the first H1 heading from content (we insert our own)."""
    return re.sub(r'^#\s+[^\n]+\n*', '', content, count=1)


def bump_headings(content: str) -> str:
    """Bump all markdown headings by one level (# -> ##, etc.)."""
    return re.sub(r'^(#+)', r'#\1', content, flags=re.MULTILINE)


def _replace_wiki_link_for_pdf(
    match: re.Match,
    known_files: set[str],
    slug_map: dict[str, str],
    docs_dir: Path,
) -> str:
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
            abs_path = docs_dir / known_path
            return f"![]({abs_path})"
        return f"![]({inner})"

    # Link with alias: [[path|alias]]
    if "|" in inner:
        target, alias = inner.split("|", 1)
        filename = target.split("/")[-1]
        if not filename.endswith(".md"):
            filename += ".md"
        known_path = _find_known_path(filename, known_files)
        if known_path and known_path in slug_map:
            return f"[{alias}](#{slug_map[known_path]})"
        return f"**{alias}**"

    # Simple link: [[Note Name]]
    filename = inner.split("/")[-1]
    display = filename
    if not filename.endswith(".md"):
        filename += ".md"
    known_path = _find_known_path(filename, known_files)
    if known_path and known_path in slug_map:
        return f"[{display}](#{slug_map[known_path]})"
    return f"**{inner}**"


def convert_wiki_links_for_pdf(
    content: str,
    known_files: set[str],
    slug_map: dict[str, str],
    docs_dir: Path,
) -> str:
    return re.sub(
        WIKI_LINK_PATTERN,
        lambda m: _replace_wiki_link_for_pdf(m, known_files, slug_map, docs_dir),
        content,
    )


def build_combined_markdown(
    docs_dir: Path, nav: list, known_files: set[str]
) -> str:
    ordered_files = flatten_nav(nav)
    slug_map = {path: slugify(title) for title, path in ordered_files}

    parts = []
    for title, rel_path in ordered_files:
        file_path = docs_dir / rel_path
        content = file_path.read_text(encoding="utf-8")

        content = convert_wiki_links_for_pdf(content, known_files, slug_map, docs_dir)
        content = strip_first_heading(content)
        content = bump_headings(content)

        slug = slug_map[rel_path]
        parts.append(f"# {title} {{#{slug}}}\n\n{content}")

    return "\n\n---\n\n".join(parts)


def export_pdf(
    source_dir: Path,
    output_path: Path,
    site_name: str,
) -> None:
    if not shutil.which("pandoc"):
        raise RuntimeError(
            "pandoc is not installed. Install it with: brew install pandoc"
        )

    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = Path(tmp) / "docs"
        _copy_source(source_dir, docs_dir)

        known_files = _collect_known_files(docs_dir)
        nav = build_nav(docs_dir)

        combined = build_combined_markdown(docs_dir, nav, known_files)

        # Prepend title page metadata for pandoc
        combined_md = Path(tmp) / "combined.md"
        combined_md.write_text(combined, encoding="utf-8")

        output_path = Path(output_path).resolve()
        cmd = [
            "pandoc", str(combined_md),
            "--from", "markdown-tex_math_dollars-subscript",
            "--toc", "--toc-depth=2",
            "--metadata", f"title={site_name}",
            "--pdf-engine=weasyprint",
            f"--css={_CSS_FILE}",
            "-o", str(output_path),
        ]
        env = os.environ.copy()
        # On macOS with Homebrew, weasyprint needs to find system libs
        if platform.system() == "Darwin":
            brew_lib = "/opt/homebrew/lib"
            if Path(brew_lib).exists():
                env["DYLD_FALLBACK_LIBRARY_PATH"] = brew_lib
        subprocess.run(cmd, check=True, env=env)
