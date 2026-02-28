from obsidian_export.nav_builder import build_nav


def _create_files(base, files):
    for f in files:
        path = base / f
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.stem}\n")


def test_basic_tree(tmp_path):
    _create_files(tmp_path, [
        "intro.md",
        "Section A/page1.md",
        "Section A/page2.md",
    ])
    nav = build_nav(tmp_path)
    # Root file + one section with 2 pages
    assert {"intro": "intro.md"} in nav
    section = next(item for item in nav if "Section A" in item)
    assert len(section["Section A"]) == 2


def test_assets_skipped(tmp_path):
    _create_files(tmp_path, [
        "page.md",
        "Assets/image.png",
        "Sub/Assets/diagram.png",
        "Sub/note.md",
    ])
    nav = build_nav(tmp_path)
    flat = str(nav)
    assert "Assets" not in flat


def test_nested_sections(tmp_path):
    _create_files(tmp_path, [
        "A/B/deep.md",
        "A/top.md",
    ])
    nav = build_nav(tmp_path)
    section_a = next(item for item in nav if "A" in item)
    # Should contain top.md and subsection B
    assert len(section_a["A"]) == 2
