from pathlib import Path
from unittest.mock import patch

import pytest

from obsidian_export.pdf_exporter import (
    bump_headings,
    build_combined_markdown,
    convert_wiki_links_for_pdf,
    export_pdf,
    flatten_nav,
    slugify,
)


class TestFlattenNav:
    def test_flat_list(self):
        nav = [{"intro": "intro.md"}, {"setup": "setup.md"}]
        assert flatten_nav(nav) == [("intro", "intro.md"), ("setup", "setup.md")]

    def test_nested_sections(self):
        nav = [
            {"Section A": [
                {"Sub B": [{"deep": "Section A/Sub B/deep.md"}]},
                {"top": "Section A/top.md"},
            ]},
            {"intro": "intro.md"},
        ]
        result = flatten_nav(nav)
        assert result == [
            ("deep", "Section A/Sub B/deep.md"),
            ("top", "Section A/top.md"),
            ("intro", "intro.md"),
        ]

    def test_empty(self):
        assert flatten_nav([]) == []


class TestSlugify:
    def test_simple(self):
        assert slugify("My Note") == "my-note"

    def test_with_hyphens(self):
        assert slugify("Agentic Applications - Architecture") == "agentic-applications---architecture"

    def test_single_word(self):
        assert slugify("note") == "note"

    def test_special_chars(self):
        assert slugify("My Note (draft)") == "my-note-draft"


class TestBumpHeadings:
    def test_bumps_all_levels(self):
        content = "# Title\n## Sub\n### Deep"
        assert bump_headings(content) == "## Title\n### Sub\n#### Deep"

    def test_leaves_non_headings_alone(self):
        content = "Just some text\nNo headings here"
        assert bump_headings(content) == content

    def test_inline_hash_not_affected(self):
        content = "Use `#anchor` in code"
        assert bump_headings(content) == content


class TestConvertWikiLinksForPdf:
    def setup_method(self):
        self.known_files = {"notes/intro.md", "notes/setup.md", "Assets/image.png"}
        self.slug_map = {
            "notes/intro.md": "intro",
            "notes/setup.md": "setup",
        }
        self.docs_dir = Path("/tmp/fake")

    def test_simple_link(self):
        result = convert_wiki_links_for_pdf(
            "See [[intro]]", self.known_files, self.slug_map, self.docs_dir
        )
        assert result == "See [intro](#intro)"

    def test_link_with_alias(self):
        result = convert_wiki_links_for_pdf(
            "See [[intro|Introduction]]", self.known_files, self.slug_map, self.docs_dir
        )
        assert result == "See [Introduction](#intro)"

    def test_dangling_link(self):
        result = convert_wiki_links_for_pdf(
            "See [[unknown]]", self.known_files, self.slug_map, self.docs_dir
        )
        assert result == "See **unknown**"

    def test_anchor_link(self):
        result = convert_wiki_links_for_pdf(
            "See [[#My Heading]]", self.known_files, self.slug_map, self.docs_dir
        )
        assert result == "See [My Heading](#my-heading)"

    def test_image_embed(self):
        result = convert_wiki_links_for_pdf(
            "![[image.png]]", self.known_files, self.slug_map, self.docs_dir
        )
        assert result == f"![]({self.docs_dir / 'Assets/image.png'})"


class TestBuildCombinedMarkdown:
    def test_combines_files_with_anchors_and_links(self, tmp_path):
        # Create a small vault structure
        (tmp_path / "intro.md").write_text("# Welcome\nSee [[details]] for more.")
        sub = tmp_path / "Section"
        sub.mkdir()
        (sub / "details.md").write_text("## Info\nBack to [[intro]].")

        nav = [
            {"Section": [{"details": "Section/details.md"}]},
            {"intro": "intro.md"},
        ]
        known_files = {"intro.md", "Section/details.md"}

        result = build_combined_markdown(tmp_path, nav, known_files)

        # Check note titles with anchors are present
        assert "# details {#details}" in result
        assert "# intro {#intro}" in result
        # Headings bumped
        assert "### Info" in result
        assert "## Welcome" in result
        # Wiki-links converted to anchors
        assert "[details](#details)" in result
        assert "[intro](#intro)" in result


class TestExportPdf:
    def test_pandoc_not_found(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        (source / "note.md").write_text("# Hello")

        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="pandoc"):
                export_pdf(source, tmp_path / "out.pdf", "Test")

    def test_calls_pandoc(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        (source / "note.md").write_text("# Hello")
        output = tmp_path / "out.pdf"

        with patch("shutil.which", return_value="/usr/local/bin/pandoc"), \
             patch("subprocess.run") as mock_run:
            export_pdf(source, output, "Test Site")

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "pandoc"
        assert "--toc" in cmd
        assert str(output) in cmd
