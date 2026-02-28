# Obsidian-to-MkDocs Export

Export a subfolder of an Obsidian vault as a branded [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) static site.

## Install

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

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

**Arguments:**

| Argument | Description |
|---|---|
| `source_folder` | Relative path within the vault (e.g. `Projects/Client/Report`) |
| `--vault` | Absolute path to the Obsidian vault root |
| `--output` | Output directory for the generated MkDocs site |
| `--site-name` | Site title displayed in the header |
| `--primary-color` | Brand color as hex (default: `#263E83`) |
| `--logo-url` | URL for the site logo (optional) |
| `--lang` | Primary language for search (default: `en`) |
| `--index` | Filename to rename as `index.md` / home page (optional) |

**Example:**

```bash
uv run obsidian-export "Projects/Client/Report" \
  --vault "/Users/me/Obsidian Vault" \
  --output ./client-site \
  --site-name "Client Report" \
  --primary-color "#263E83" \
  --index "Report - Overview.md"
```

## Serve locally

After exporting, preview the site with:

```bash
cd client-site
uv run mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

## What it does

1. Copies the source folder into `<output>/docs/`
2. Converts Obsidian wiki-links (`[[...]]`) to standard markdown links
3. Turns dangling links (targets outside the exported folder) into bold text
4. Renames the specified index file to `index.md`
5. Generates `mkdocs.yml` with Material theme and brand colors
6. Runs `mkdocs build` to produce the static site in `<output>/site/`

## Tests

```bash
uv run pytest
```
