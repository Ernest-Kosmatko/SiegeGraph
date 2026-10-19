# SiegeGraph

Attack-path mapping and evidence management for authorized penetration
testing engagements.

SiegeGraph tracks what a tester already knows — hosts, services,
vulnerabilities, credentials, pivots — as a directed graph, attaches
hashed evidence to each step, and renders the kill chain and findings
straight into a report. It does not scan or exploit anything itself; it
organizes the output of the tools you already use.

## Features

- Directed attack-path graph: host → service → vulnerability → credential → pivot → objective
- Content-addressed evidence store (SHA-256 per file, tamper-evident)
- Kill-chain path queries (`host` → `objective`) over the current graph
- Markdown report generation with an embedded Mermaid diagram
- Optional AI advisor layer: local Ollama by default, with opt-in
  Anthropic, OpenAI, or Gemini backends per engagement
- Single-file SQLite project per engagement — easy to archive, encrypt, or wipe

## Installation

```bash
pip install -e .
```

Requires Python 3.10+.

## Usage

```bash
# Start a new engagement
siegegraph init acme.siege --name "Acme Corp - External Pentest" \
    --client "Acme Corp" --authorized-by "J. Smith (CISO)" --scope "10.10.10.0/24"

# Record what you find
siegegraph node add -p acme.siege -t host -l 10.10.10.5
siegegraph node add -p acme.siege -t service -l "smb/445"
siegegraph node add -p acme.siege -t vulnerability -l "MS17-010"

siegegraph edge add -p acme.siege -s <host_id> -t <service_id> --type exposes
siegegraph edge add -p acme.siege -s <vuln_id> -t <service_id> --type affects

# Attach proof
siegegraph evidence add -p acme.siege -n <vuln_id> -d "nmap script output" -f scan.txt

# Visualize and report
siegegraph graph -p acme.siege --out attack_path.mmd
siegegraph report -p acme.siege --out report.md
```

## AI Advisor (optional)

```bash
siegegraph ai advise -p acme.siege -n <vuln_id> --backend ollama
```

The advisor is given only the node and evidence already stored in the
engagement file — never live network data — and its suggestions are never
executed automatically. Every call is logged in the project's `ai_log`
table so a client can audit exactly what was sent to which provider. See
[`docs/ai-advisor.md`](docs/ai-advisor.md) and
[`config/providers.example.yaml`](config/providers.example.yaml).

Default backend is local Ollama: no API key, no external request. Cloud
backends (Anthropic, OpenAI, Gemini) are opt-in per engagement and require
their respective API keys as environment variables.

## Architecture

```
ingest (manual / scripted) → core.graph (SQLite + networkx)
                                   │
                    ┌──────────────┼──────────────┐
                 evidence       ai.router        export
                 (hashed        (optional,       (mermaid,
                  files)        logged calls)     markdown)
```

See [`docs/methodology.md`](docs/methodology.md) for the data model and
design rationale.

## Legal notice

SiegeGraph is intended for use only in engagements with documented,
written authorization from the system owner. The `authorized_by` and
`scope_note` fields exist to keep that record attached to the data itself.
Misuse against systems you do not have permission to test is illegal.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
