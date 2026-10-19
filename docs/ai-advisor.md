# AI Advisor

SiegeGraph can optionally query a language model for suggestions while
you work through an engagement. This document covers data handling,
configuration, and how to add a new backend.

## Data handling

- The advisor receives exactly one rendered prompt: the selected node's
  stored attributes plus its evidence descriptions. No live scan traffic,
  no files outside the project, no other nodes.
- Every call (prompt and response) is written to the `ai_log` table in
  the engagement's `.siege` file, so it travels with the engagement
  record for later audit.
- Nothing returned by an advisor is executed. Output is printed to the
  terminal for the operator to read and act on manually.

## Choosing a backend per engagement

Copy `config/providers.example.yaml` to `config/providers.yaml` and set
`default_backend`. For clients whose authorization or NDA restricts data
leaving the tester's machine, keep `ollama` as the only allowed backend
and do not export the relevant API key environment variables.

| Backend | Requires | Data leaves the machine? |
|---|---|---|
| `ollama` | A local Ollama install | No |
| `anthropic` | `ANTHROPIC_API_KEY` | Yes |
| `openai` | `OPENAI_API_KEY` | Yes |
| `gemini` | `GEMINI_API_KEY` | Yes |

## Adding a backend

Implement `siegegraph.ai.base.AdvisorProvider` (one method, `advise`),
register it in `siegegraph/ai/router.py`'s `_REGISTRY`, and it is
immediately available via `--backend <name>` on `siegegraph ai advise`.
