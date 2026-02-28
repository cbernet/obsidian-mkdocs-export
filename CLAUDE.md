# CLAUDE.md

## Project

- See BRIEF.md

## Tech stack

- Python 3.13, managed with uv
- pytest for tests

## Commands

```bash
uv sync              # install deps
uv run pytest        # run tests
```

## test-driven development

- start in plan mode when I ask you to do something
- write new unit tests first
- run the tests to make sure they fail
- write the code
- make sure the tests pass by editing the code
- run the tests when you're done editing

When you're working on a new functionality, if existing tests fail, don't modify the tests, modify the code to make sure tests pass.

Do not overdo tests :

- group tests that can be grouped together
- don't test trivial things, only business logic

## Managing our interactions

- feel free to disagree with me (even strongly), I'm not that sensitive and I don't know everything. 
- propose updates to CLAUDE.md based on our discussion, but keep this file simple.
- propose updates to the README.md

## Code style

- Clean, simple Python. No overengineering.
- Functions should be atomic.
- No unnecessary abstractions — a few similar lines are better than a premature helper.
- Type hints on function signatures, not on every local variable.
- No docstrings on obvious functions. Comments only where logic isn't self-evident.
- Flat module structure unless there's a clear reason to nest.
- Use stdlib when it's enough. Add a dependency only when it earns its place.

## Project structure

- `src/obsidian_export/` — source code
- `tests/` — pytest tests, mirror the src structure
- `pyproject.toml` — project config, dependencies, CLI entry points

## Key decisions

- Custom wiki-link conversion in Python, not the `roamlinks` mkdocs plugin (doesn't handle vault-absolute paths or dangling links)
- argparse over click, string.Template/f-strings over jinja2 — stdlib is enough
- Only external deps: mkdocs, mkdocs-material
