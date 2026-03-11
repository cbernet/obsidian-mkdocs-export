import json
import os

import anthropic
from dotenv import load_dotenv

_client = None

DEFAULT_MODEL = "claude-sonnet-4-6"


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        load_dotenv()
        _client = anthropic.Anthropic()
    return _client


def order_entries(entries: list[dict]) -> list[str]:
    """Ask Claude to order entries logically. Returns list of titles."""
    client = _get_client()
    model = os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL)

    user_content = (
        "Order these documentation pages in the best reading order. "
        "Return a JSON array of titles, nothing else.\n\n"
        + json.dumps(entries, indent=2)
    )

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system="You order documentation pages logically for a reader.",
        messages=[{"role": "user", "content": user_content}],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            }
        },
    )

    return json.loads(response.content[0].text)
