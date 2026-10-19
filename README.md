# ⛭ SiegeGraph

> **Attack-Path Mapping & Evidence Management**
> A graph-based engagement tracker for authorized penetration testing — map the kill chain, hash the evidence, draft the report.

[![CI](https://github.com/Ernest-Kosmatko/SiegeGraph/actions/workflows/ci.yml/badge.svg)](https://github.com/Ernest-Kosmatko/SiegeGraph/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🔍 What is SiegeGraph?

SiegeGraph is a local-first engagement tracker for **authorized** penetration tests. It does not scan or exploit anything — it organizes what you already found with your other tools:

- **Attack-Path Graph** — hosts, services, vulnerabilities, credentials, pivots, and objectives as a directed graph
- **Kill-Chain Queries** — trace every path from an entry point to an objective (e.g. host → domain admin)
- **Evidence Store** — files are hashed (SHA-256) on ingest, so nothing attached to a finding can be altered later unnoticed
- **Report Generation** — one command turns the graph + evidence into a Markdown report with an embedded diagram
- **AI Advisor (optional)** — ask a model for attack-vector suggestions using only data already in the engagement file; local by default, cloud providers opt-in
- **Single-file projects** — one SQLite file per engagement, trivial to archive or encrypt

Built on Python stdlib + a small, auditable dependency set (`networkx`, `typer`, `httpx`).

---

## 📸 Sample Session

```
$ siegegraph init acme.siege --name "Acme Corp - External Pentest" \
      --client "Acme Corp" --authorized-by "J. Smith (CISO)" --scope "10.10.10.0/24"
[+] Engagement created: acme.siege

$ siegegraph node add -p acme.siege -t host -l 10.10.10.5
[+] Added host: host_07ded3178d  (10.10.10.5)

$ siegegraph node add -p acme.siege -t vulnerability -l "MS17-010"
[+] Added vulnerability: vuln_7716e312b4  (MS17-010)

$ siegegraph edge add -p acme.siege -s vuln_7716e312b4 -t host_07ded3178d --type affects
[+] Linked: vuln_7716e312b4 -[affects]-> host_07ded3178d

$ siegegraph evidence add -p acme.siege -n vuln_7716e312b4 -d "nmap smb-vuln-ms17-010 output" -f scan.txt
[+] Evidence recorded for vuln_7716e312b4

$ siegegraph report -p acme.siege --out report.md
[+] Report written: report.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- An engagement **you are explicitly authorized, in writing, to test**

### Installation

```bash
# Clone the repository
git clone https://github.com/Ernest-Kosmatko/SiegeGraph.git
cd SiegeGraph

# Install (creates the `siegegraph` CLI command)
pip install -e .
```

### Usage

```bash
# Start a new engagement
siegegraph init acme.siege --name "Acme Corp - External Pentest" --client "Acme Corp"

# Build the attack-path graph as you go
siegegraph node add -p acme.siege -t host -l 10.10.10.5
siegegraph node add -p acme.siege -t service -l "smb/445"
siegegraph edge add -p acme.siege -s <host_id> -t <service_id> --type exposes

# Attach proof, hashed on ingest
siegegraph evidence add -p acme.siege -n <vuln_id> -d "scan output" -f scan.txt

# Visualize and report
siegegraph graph -p acme.siege --out attack_path.mmd
siegegraph report -p acme.siege --out report.md

# Optional: ask an AI advisor for next steps on one node
siegegraph ai advise -p acme.siege -n <vuln_id> --backend ollama
```

### All Commands

| Command | Description |
|---|---|
| `siegegraph init` | Create a new engagement file |
| `siegegraph node add / list` | Add or list graph nodes |
| `siegegraph edge add` | Link two nodes along the kill chain |
| `siegegraph evidence add` | Attach a hashed file + description to a node |
| `siegegraph graph` | Render the attack path as Mermaid |
| `siegegraph report` | Generate the Markdown report |
| `siegegraph ai advise` | Query an AI advisor about one node |

---

## 🧠 AI Advisor

SiegeGraph can optionally query a language model for suggestions while you work, using only data already stored in the engagement file — never live network traffic, never other projects.

| Backend | Requires | Data leaves the machine? |
|---|---|---|
| `ollama` (default) | Local Ollama install | No |
| `anthropic` | `ANTHROPIC_API_KEY` | Yes |
| `openai` | `OPENAI_API_KEY` | Yes |
| `gemini` | `GEMINI_API_KEY` | Yes |

Every call is logged in the project's own `ai_log` table for client-side audit, and nothing an advisor returns is ever executed automatically — it is printed for the operator to review. See [`docs/ai-advisor.md`](docs/ai-advisor.md).

---

## 🧠 Use as a Library

```python
from siegegraph.core.graph import Project
from siegegraph.core.models import Engagement, Node, NodeType, Edge, EdgeType
from siegegraph.export.report import build

p = Project("acme.siege")
p.create_engagement(Engagement(name="Acme Corp Pentest", client="Acme Corp"))

host = p.add_node(Node(type=NodeType.HOST, label="10.10.10.5"))
vuln = p.add_node(Node(type=NodeType.VULNERABILITY, label="MS17-010"))
p.add_edge(Edge(source=vuln.id, target=host.id, type=EdgeType.AFFECTS))

print(build(p))  # full Markdown report, mermaid diagram included
```

---

## 🏗️ Project Structure

```
SiegeGraph/
├── siegegraph/
│   ├── core/              # Graph model + SQLite persistence
│   │   ├── models.py      # Node, Edge, Evidence, Engagement
│   │   └── graph.py       # Project store, kill-chain queries
│   ├── evidence/
│   │   └── store.py       # Content-addressed (SHA-256) evidence files
│   ├── export/
│   │   ├── mermaid.py     # Attack-path diagram rendering
│   │   └── report.py      # Markdown report generation
│   ├── ai/
│   │   ├── base.py        # AdvisorProvider contract
│   │   ├── router.py      # Backend selection + audit logging
│   │   └── providers/     # ollama, anthropic, openai, gemini
│   ├── db/
│   │   └── schema.sql     # SQLite schema
│   └── cli.py             # CLI entry point (Typer)
├── tests/                 # pytest suite
├── docs/
│   ├── methodology.md     # Data model & design rationale
│   └── ai-advisor.md      # AI advisor data handling
├── config/
│   └── providers.example.yaml
├── .github/workflows/ci.yml
├── pyproject.toml
└── README.md
```

---

## 🧪 Running Tests

```bash
pip install -e . pytest
pytest tests/ -v
```

---

## ⚠️ Legal Disclaimer

**This tool is for authorized security testing only.**
Using SiegeGraph to document activity against systems you do not have explicit, written permission to test is illegal under the Computer Fraud and Abuse Act (CFAA), the UK Computer Misuse Act, and equivalent laws worldwide.

The author assumes no liability for misuse of this software.
**Always get written authorization before testing any target.**

---

## 📄 License

[MIT](LICENSE) © Ernest Kosmatko

---

## 👤 Author

**Ernest Kosmatko**
GitHub: [@Ernest-Kosmatko](https://github.com/Ernest-Kosmatko)
