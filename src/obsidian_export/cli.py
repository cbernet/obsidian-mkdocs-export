import argparse
from pathlib import Path

from obsidian_export.exporter import export
from obsidian_export.pdf_exporter import export_pdf


def _validate_source_dir(source_dir: Path, vault: Path) -> None:
    resolved = source_dir.resolve()
    vault_resolved = vault.resolve()
    if not resolved.is_relative_to(vault_resolved):
        raise ValueError(f"Source folder is outside the vault: {source_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Export an Obsidian vault subfolder as a branded MkDocs Material site."
    )
    parser.add_argument("source_folder", help="Relative path within the vault (e.g. 'Projects/Client/Report')")
    parser.add_argument("--vault", required=True, type=Path, help="Path to the Obsidian vault root")
    parser.add_argument("--output", type=Path, default=None, help="Output directory for the MkDocs site")
    parser.add_argument("--site-name", required=True, help="Site title in the generated site")
    parser.add_argument("--primary-color", default="#263E83", help="Primary brand color (hex)")
    parser.add_argument("--logo-url", default=None, help="URL for the site logo")
    parser.add_argument("--lang", default="en", help="Primary language for search (default: en)")
    parser.add_argument("--index", default=None, dest="index_file", help="Filename to rename as index.md (e.g. 'Home.md')")
    parser.add_argument("--pdf", action="store_true", help="Generate a single PDF instead of an MkDocs site")
    parser.add_argument("--pdf-output", type=Path, default=None, help="Output PDF file path (default: <site-name>.pdf)")

    args = parser.parse_args()
    source_dir = args.vault / args.source_folder
    _validate_source_dir(source_dir, args.vault)

    if args.pdf:
        pdf_path = args.pdf_output or Path(f"{args.site_name}.pdf")
        export_pdf(
            source_dir=source_dir,
            output_path=pdf_path,
            site_name=args.site_name,
        )
    else:
        if not args.output:
            parser.error("--output is required when not using --pdf")
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
