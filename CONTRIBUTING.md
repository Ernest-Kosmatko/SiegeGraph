# Contributing

## Setup

```bash
pip install -e ".[dev]"
pytest
```

## Guidelines

- Keep the core graph model (`siegegraph/core/`) free of network and
  process side effects — it must stay trivially testable.
- New AI backends go in `siegegraph/ai/providers/` and implement
  `AdvisorProvider` from `siegegraph/ai/base.py`. Register them in
  `siegegraph/ai/router.py`.
- New export formats go in `siegegraph/export/` and take a `Project` in,
  return a string or write a file — no CLI logic inside them.
- Run `pytest` before opening a pull request. Add a test for any new
  node/edge type or export format.

## Pull requests

Describe the engagement workflow your change improves, not just the code
change. Screenshots of rendered Mermaid output are welcome for anything
touching `export/`.
