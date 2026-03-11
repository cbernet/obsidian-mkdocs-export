from unittest.mock import patch, MagicMock

from obsidian_export.nav_builder import build_nav
from obsidian_export.llm_ordering import order_entries


def _create_files(base, file_contents: dict[str, str]):
    """Create files with specific content."""
    for name, content in file_contents.items():
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def test_order_entries_calls_api_and_parses_response():
    """order_entries sends entries to Claude and returns ordered titles."""
    entries = [
        {"title": "advanced", "summary": "Advanced topics"},
        {"title": "intro", "summary": "Getting started"},
    ]
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='["intro", "advanced"]')]
    mock_response.stop_reason = "end_turn"

    with patch("obsidian_export.llm_ordering._get_client") as mock_get:
        mock_client = MagicMock()
        mock_get.return_value = mock_client
        mock_client.messages.create.return_value = mock_response
        result = order_entries(entries)

    assert result == ["intro", "advanced"]


def test_build_nav_with_llm_order(tmp_path):
    """LLM ordering reorders files at each directory level."""
    _create_files(tmp_path, {
        "zebra.md": "# Zebra\nThis comes last alphabetically but first logically.",
        "alpha.md": "# Alpha\nThis comes first alphabetically but second logically.",
    })

    def fake_order(entries):
        return ["zebra", "alpha"]

    with patch("obsidian_export.llm_ordering.order_entries", fake_order):
        nav = build_nav(tmp_path, llm_order=True)

    titles = [list(item.keys())[0] for item in nav]
    assert titles == ["zebra", "alpha"]


def test_build_nav_llm_fallback_for_missing_entries(tmp_path):
    """Entries not in LLM response go at the end, alphabetically."""
    _create_files(tmp_path, {
        "charlie.md": "# Charlie",
        "alpha.md": "# Alpha",
        "bravo.md": "# Bravo",
    })

    def fake_order(entries):
        # LLM only returns bravo, misses alpha and charlie
        return ["bravo"]

    with patch("obsidian_export.llm_ordering.order_entries", fake_order):
        nav = build_nav(tmp_path, llm_order=True)

    titles = [list(item.keys())[0] for item in nav]
    assert titles == ["bravo", "alpha", "charlie"]


def test_build_nav_without_llm_unchanged(tmp_path):
    """Default behavior (no LLM) is unchanged: dirs first, alphabetical."""
    _create_files(tmp_path, {
        "beta.md": "# Beta",
        "alpha.md": "# Alpha",
    })
    nav = build_nav(tmp_path)
    titles = [list(item.keys())[0] for item in nav]
    assert titles == ["alpha", "beta"]
