import yaml


def generate_mkdocs_yml(site_name: str, nav: list, primary_color: str, logo_url: str | None = None, lang: str = "en") -> str:
    config = {
        "site_name": site_name,
        "theme": {
            "name": "material",
            "palette": [
                {"scheme": "default", "toggle": {"icon": "material/brightness-7", "name": "Switch to dark mode"}},
                {"scheme": "slate", "toggle": {"icon": "material/brightness-4", "name": "Switch to light mode"}},
            ],
            "features": [
                "navigation.instant",
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
            ],
        },
        "extra_css": ["stylesheets/extra.css"],
        "plugins": [
            {"search": {"lang": [lang, "en"] if lang != "en" else ["en"]}},
        ],
        "nav": nav,
    }

    if logo_url:
        config["theme"]["logo"] = logo_url

    return yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_extra_css(primary_color: str) -> str:
    return (
        ":root {\n"
        f"  --md-primary-fg-color: {primary_color};\n"
        "}\n"
    )
