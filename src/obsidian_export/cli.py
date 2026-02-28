import argparse
from pathlib import Path

from obsidian_export.exporter import export


def main():
    parser = argparse.ArgumentParser(
        description="Export an Obsidian vault subfolder as a branded MkDocs Material site."
    )
    parser.add_argument("source_folder", help="Relative path within the vault (e.g. 'Projects/Client/Report')")
    parser.add_argument("--vault", required=True, type=Path, help="Path to the Obsidian vault root")
    parser.add_argument("--output", required=True, type=Path, help="Output directory for the MkDocs site")
    parser.add_argument("--site-name", required=True, help="Site title in the generated site")
    parser.add_argument("--primary-color", default="#263E83", help="Primary brand color (hex)")
    parser.add_argument("--logo-url", default=None, help="URL for the site logo")
    parser.add_argument("--lang", default="en", help="Primary language for search (default: en)")
    parser.add_argument("--index", default=None, dest="index_file", help="Filename to rename as index.md (e.g. 'Home.md')")

    args = parser.parse_args()
    source_dir = args.vault / args.source_folder

    export(
        source_dir=source_dir,
        output_dir=args.output,
        site_name=args.site_name,
        primary_color=args.primary_color,
        logo_url=args.logo_url,
        lang=args.lang,
        index_file=args.index_file,
    )


if __name__ == "__main__":
    main()
