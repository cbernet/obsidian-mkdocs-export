import re
import shutil
import subprocess
from pathlib import Path

from obsidian_export.config_generator import generate_extra_css, generate_mkdocs_yml
from obsidian_export.link_converter import convert_wiki_links
from obsidian_export.nav_builder import build_nav

EXCLUDE = {".DS_Store", ".obsidian"}
_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _collect_known_files(docs_dir: Path) -> set[str]:
    known = set()
    for path in docs_dir.rglob("*"):
        if path.is_file() and not any(part in EXCLUDE for part in path.parts):
            known.add(str(path.relative_to(docs_dir)))
    return known


def _copy_source(source_dir: Path, docs_dir: Path) -> None:
    shutil.copytree(
        source_dir,
        docs_dir,
        ignore=shutil.ignore_patterns(*EXCLUDE),
    )


def _convert_all_links(docs_dir: Path, known_files: set[str]) -> None:
    for md_file in docs_dir.rglob("*.md"):
        current_file = str(md_file.relative_to(docs_dir))
        content = md_file.read_text(encoding="utf-8")
        converted = convert_wiki_links(content, known_files, current_file)
        md_file.write_text(converted, encoding="utf-8")


def _rename_index(docs_dir: Path, index_file: str) -> None:
    source = (docs_dir / index_file).resolve()
    if not source.is_relative_to(docs_dir.resolve()):
        raise ValueError(f"Index file '{index_file}' escapes docs directory")
    if source.exists():
        source.rename(docs_dir / "index.md")


def export(
    source_dir: Path,
    output_dir: Path,
    site_name: str,
    primary_color: str,
    logo_url: str | None = None,
    lang: str = "en",
    index_file: str | None = None,
    build: bool = True,
    llm_order: bool = False,
) -> None:
    if not _HEX_COLOR_RE.match(primary_color):
        raise ValueError(f"Invalid hex color: {primary_color}")

    docs_dir = output_dir / "docs"

    _copy_source(source_dir, docs_dir)

    known_files = _collect_known_files(docs_dir)
    _convert_all_links(docs_dir, known_files)

    if index_file:
        _rename_index(docs_dir, index_file)

    # Generate extra CSS
    css_dir = docs_dir / "stylesheets"
    css_dir.mkdir(parents=True, exist_ok=True)
    (css_dir / "extra.css").write_text(generate_extra_css(primary_color))

    # Generate mkdocs.yml
    nav = build_nav(docs_dir, llm_order=llm_order)
    yml_content = generate_mkdocs_yml(site_name, nav, primary_color, logo_url, lang)
    (output_dir / "mkdocs.yml").write_text(yml_content)

    # Generate pyproject.toml for Cloudflare Pages builds
    (output_dir / "pyproject.toml").write_text(
        '[project]\nname = "site"\nversion = "0.1.0"\nrequires-python = ">=3.12"\n'
        'dependencies = [\n    "mkdocs>=1.6",\n    "mkdocs-material>=9.5",\n]\n'
    )

    # Generate .gitignore
    (output_dir / ".gitignore").write_text("site/\n")

    if build:
        subprocess.run(["mkdocs", "build"], cwd=output_dir, check=True)
