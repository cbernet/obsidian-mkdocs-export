from obsidian_export.link_converter import convert_wiki_links


KNOWN_FILES = {
    "Agentic Applications - Architecture.md",
    "Interviews/CR_Interview_Jeremy.md",
    "Assets/app-infrastructure_basic.png",
    "Assets/application_internals.png",
    "Agentic Platform/Assets/diagram.png",
}


def test_simple_link_to_known_file():
    content = "See [[Agentic Applications - Architecture]] for details."
    result = convert_wiki_links(content, KNOWN_FILES, "index.md")
    assert result == "See [Agentic Applications - Architecture](Agentic%20Applications%20-%20Architecture.md) for details."


def test_path_with_alias():
    content = "See [[Some/Deep/Path/CR_Interview_Jeremy|Jeremy's interview]]."
    result = convert_wiki_links(content, KNOWN_FILES, "index.md")
    assert result == "See [Jeremy's interview](Interviews/CR_Interview_Jeremy.md)."


def test_anchor_link():
    content = "Jump to [[#Software framework options]]."
    result = convert_wiki_links(content, KNOWN_FILES, "index.md")
    assert result == "Jump to [Software framework options](#software-framework-options)."


def test_image_embed_from_root():
    """Image at Assets/ referenced from a root-level file — path stays the same."""
    content = "Diagram: ![[Some/Deep/Assets/app-infrastructure_basic.png]]"
    result = convert_wiki_links(content, KNOWN_FILES, "index.md")
    assert result == "Diagram: ![](Assets/app-infrastructure_basic.png)"


def test_image_embed_from_subdir():
    """Image at Agentic Platform/Assets/ referenced from a file in Agentic Platform/ — relative path."""
    content = "Diagram: ![[Some/Deep/Assets/diagram.png]]"
    result = convert_wiki_links(content, KNOWN_FILES, "Agentic Platform/page.md")
    assert result == "Diagram: ![](Assets/diagram.png)"


def test_image_embed_cross_directory():
    """Image at Assets/ (root) referenced from a file in Agentic Platform/ — needs ../"""
    content = "See ![[Assets/application_internals.png]]"
    result = convert_wiki_links(content, KNOWN_FILES, "Agentic Platform/page.md")
    assert result == "See ![](../Assets/application_internals.png)"


def test_dangling_link():
    content = "Related: [[RAG - Semantic Search]] is important."
    result = convert_wiki_links(content, KNOWN_FILES, "index.md")
    assert result == "Related: **RAG - Semantic Search** is important."


def test_mixed_content():
    content = (
        "See [[Agentic Applications - Architecture]] and [[RAG - Semantic Search]].\n"
        "Image: ![[Assets/application_internals.png]]\n"
        "Jump to [[#Software framework options]]."
    )
    result = convert_wiki_links(content, KNOWN_FILES, "index.md")
    expected = (
        "See [Agentic Applications - Architecture](Agentic%20Applications%20-%20Architecture.md) and **RAG - Semantic Search**.\n"
        "Image: ![](Assets/application_internals.png)\n"
        "Jump to [Software framework options](#software-framework-options)."
    )
    assert result == expected


def test_no_wiki_links():
    content = "Plain markdown with [regular link](https://example.com)."
    result = convert_wiki_links(content, KNOWN_FILES, "index.md")
    assert result == content
