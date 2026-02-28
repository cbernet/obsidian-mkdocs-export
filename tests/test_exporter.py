import pytest

from obsidian_export.exporter import export, _rename_index


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

    # pyproject.toml generated for Cloudflare Pages
    pyproject = output / "pyproject.toml"
    assert pyproject.exists()
    pyproject_text = pyproject.read_text()
    assert "mkdocs" in pyproject_text
    assert "mkdocs-material" in pyproject_text

    # .gitignore generated
    gitignore = output / ".gitignore"
    assert gitignore.exists()
    assert "site/" in gitignore.read_text()


def test_rename_index_path_traversal(tmp_path):
    """_rename_index must reject paths that escape docs_dir."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    # Create a file outside docs_dir that the traversal would target
    secret = tmp_path / "secret.md"
    secret.write_text("sensitive data")

    with pytest.raises(ValueError, match="escapes"):
        _rename_index(docs_dir, "../secret.md")

    # The file outside must be untouched
    assert secret.exists()
    assert not (docs_dir / "index.md").exists()


def test_export_rejects_source_escaping_vault(tmp_path):
    """export must reject source_dir that is not inside a reasonable boundary."""
    # source_dir points outside the vault — should raise
    vault = tmp_path / "vault"
    vault.mkdir()
    source_dir = tmp_path / "vault" / ".." / "etc"
    source_dir = source_dir.resolve()
    source_dir.mkdir(exist_ok=True)
    (source_dir / "passwd.md").write_text("root:x:0:0")

    # The CLI builds source_dir = vault / source_folder, so a traversal
    # would produce a path not under vault. We test the CLI-level validation.
    from obsidian_export.cli import _validate_source_dir
    with pytest.raises(ValueError, match="outside"):
        _validate_source_dir(source_dir, vault)


def test_export_rejects_bad_primary_color(tmp_path):
    """export must reject primary_color that isn't a valid hex color."""
    source = _create_fake_vault(tmp_path / "vault")
    output = tmp_path / "site"

    with pytest.raises(ValueError, match="color"):
        export(
            source_dir=source,
            output_dir=output,
            site_name="Test",
            primary_color="red;}body{display:none",
            build=False,
        )
