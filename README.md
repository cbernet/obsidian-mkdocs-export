# Obsidian-to-MkDocs Export

Export a subfolder of an Obsidian vault as a branded [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) static site, or as a single PDF with table of contents and working internal links.

## Install

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

### PDF export dependencies

PDF export requires [pandoc](https://pandoc.org/) and system libraries for [weasyprint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) (the PDF rendering engine). Weasyprint itself is installed automatically via `uv sync`.

On macOS:

```bash
brew install pandoc pango gdk-pixbuf
```

On Debian/Ubuntu:

```bash
sudo apt install pandoc libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

## Usage

### MkDocs site export

```bash
uv run obsidian-export <source_folder> \
  --vault <path_to_vault> \
  --output <output_dir> \
  --site-name <title> \
  [--primary-color "#263E83"] \
  [--logo-url <url>] \
  [--lang en] \
  [--index <filename.md>]
```

**Example:**

```bash
uv run obsidian-export "Projects/Client/Report" \
  --vault "/Users/me/Obsidian Vault" \
  --output ./client-site \
  --site-name "Client Report" \
  --primary-color "#263E83" \
  --index "Report - Overview.md"
```

### PDF export

```bash
uv run obsidian-export <source_folder> \
  --vault <path_to_vault> \
  --site-name <title> \
  --pdf \
  [--pdf-output <output.pdf>]
```

**Example:**

```bash
uv run obsidian-export "Projects/Client/Report" \
  --vault "/Users/me/Obsidian Vault" \
  --site-name "Client Report" \
  --pdf \
  --pdf-output "Client Report.pdf"
```

The PDF includes a table of contents, styled headings, and internal links that navigate within the document. If `--pdf-output` is omitted, the file is named after the site name.

### Arguments

| Argument | Description |
|---|---|
| `source_folder` | Relative path within the vault (e.g. `Projects/Client/Report`) |
| `--vault` | Path to the Obsidian vault root |
| `--output` | Output directory for the MkDocs site (required unless `--pdf`) |
| `--site-name` | Site title |
| `--primary-color` | Brand color as hex (default: `#263E83`) |
| `--logo-url` | URL for the site logo (optional) |
| `--lang` | Primary language for search (default: `en`) |
| `--index` | Filename to rename as `index.md` / home page (optional) |
| `--pdf` | Generate a single PDF instead of an MkDocs site |
| `--pdf-output` | Output PDF file path (default: `<site-name>.pdf`) |

## Serve locally

After a site export, preview it with:

```bash
cd client-site
uv run mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

## What it does

### Site export

1. Copies the source folder into `<output>/docs/`
2. Converts Obsidian wiki-links (`[[...]]`) to standard markdown links
3. Turns dangling links (targets outside the exported folder) into bold text
4. Renames the specified index file to `index.md`
5. Generates `mkdocs.yml` with Material theme and brand colors
6. Runs `mkdocs build` to produce the static site in `<output>/site/`

### PDF export

1. Copies the source folder to a temporary directory
2. Builds a navigation order from the directory structure (directories first, alphabetically)
3. Converts wiki-links to internal `#anchor` references
4. Concatenates all notes into a single document with heading hierarchy
5. Runs pandoc with weasyprint to produce a styled PDF with table of contents

## Tests

```bash
uv run pytest
```
