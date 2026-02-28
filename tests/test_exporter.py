from obsidian_export.exporter import export


def _create_fake_vault(base):
    """Create a minimal fake vault structure."""
    files = {
        "Home.md": "# Home\nSee [[Topic A]] and [[Missing Page]].\n",
        "Topic A.md": "# Topic A\nImage: ![[Assets/diagram.png]]\n",
        "Assets/diagram.png": "fake-png-data",
        "Sub/nested.md": "# Nested\nBack to [[Home]].\n",
        ".DS_Store": "junk",
    }
    for path, content in files.items():
        full = base / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
    return base


def test_export_pipeline(tmp_path):
    source = _create_fake_vault(tmp_path / "vault")
    output = tmp_path / "site"

    export(
        source_dir=source,
        output_dir=output,
        site_name="Test Site",
        primary_color="#FF0000",
        logo_url=None,
        lang="en",
        index_file="Home.md",
        build=False,
    )

    docs = output / "docs"

    # Files copied, .DS_Store excluded
    assert (docs / "Topic A.md").exists()
    assert (docs / "Assets" / "diagram.png").exists()
    assert not (docs / ".DS_Store").exists()

    # Index file renamed
    assert (docs / "index.md").exists()
    assert not (docs / "Home.md").exists()

    # Wiki-links converted
    index_content = (docs / "index.md").read_text()
    assert "[[" not in index_content
    assert "Topic A" in index_content
    assert "**Missing Page**" in index_content

    # mkdocs.yml generated
    mkdocs_yml = output / "mkdocs.yml"
    assert mkdocs_yml.exists()
    assert "Test Site" in mkdocs_yml.read_text()

    # extra.css generated
    css = docs / "stylesheets" / "extra.css"
    assert css.exists()
    assert "#FF0000" in css.read_text()
