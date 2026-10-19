from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from siegegraph.core.graph import Project
from siegegraph.core.models import Edge, EdgeType, Engagement, Evidence, Node, NodeType
from siegegraph.evidence.store import ingest_file
from siegegraph.export.mermaid import render as render_mermaid
from siegegraph.export.report import build as build_report

app = typer.Typer(help="SiegeGraph: attack-path mapping for authorized engagements.")
node_app = typer.Typer(help="Manage graph nodes.")
edge_app = typer.Typer(help="Manage graph edges.")
evidence_app = typer.Typer(help="Attach and list evidence.")
ai_app = typer.Typer(help="Optional AI advisor (opt-in, see docs/ai-advisor.md).")
app.add_typer(node_app, name="node")
app.add_typer(edge_app, name="edge")
app.add_typer(evidence_app, name="evidence")
app.add_typer(ai_app, name="ai")

console = Console()


def _open(project: str) -> Project:
    return Project(project)


@app.command()
def init(
    project: str = typer.Argument(..., help="Path to the new .siege project file."),
    name: str = typer.Option(..., help="Engagement name."),
    client: str = typer.Option("", help="Client name."),
    authorized_by: str = typer.Option("", help="Who signed the authorization."),
    scope: str = typer.Option("", help="One-line scope note."),
) -> None:
    """Create a new engagement file."""
    if Path(project).exists():
        typer.echo(f"{project} already exists.", err=True)
        raise typer.Exit(1)
    p = _open(project)
    p.create_engagement(Engagement(name=name, client=client, authorized_by=authorized_by, scope_note=scope))
    console.print(f"[green]Engagement created:[/green] {project}")


@node_app.command("add")
def node_add(
    project: str = typer.Option(..., "--project", "-p"),
    type: NodeType = typer.Option(..., "--type", "-t"),
    label: str = typer.Option(..., "--label", "-l"),
    attr: list[str] = typer.Option([], "--attr", help="key=value, repeatable"),
) -> None:
    """Add a node (host/service/vulnerability/credential/pivot/objective)."""
    p = _open(project)
    attrs = dict(a.split("=", 1) for a in attr)
    node = p.add_node(Node(type=type, label=label, attributes=attrs))
    console.print(f"[green]Added {type.value}:[/green] {node.id}  ({label})")


@node_app.command("list")
def node_list(project: str = typer.Option(..., "--project", "-p")) -> None:
    p = _open(project)
    table = Table(title="Nodes")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Label")
    for row in p.list_nodes():
        table.add_row(row["id"], row["type"], row["label"])
    console.print(table)


@edge_app.command("add")
def edge_add(
    project: str = typer.Option(..., "--project", "-p"),
    source: str = typer.Option(..., "--source", "-s"),
    target: str = typer.Option(..., "--target", "-t"),
    type: EdgeType = typer.Option(..., "--type"),
    note: str = typer.Option("", "--note"),
) -> None:
    """Link two nodes to extend the kill chain."""
    p = _open(project)
    edge = p.add_edge(Edge(source=source, target=target, type=type, note=note))
    console.print(f"[green]Linked:[/green] {source} -[{type.value}]-> {target}")


@evidence_app.command("add")
def evidence_add(
    project: str = typer.Option(..., "--project", "-p"),
    node: str = typer.Option(..., "--node", "-n"),
    description: str = typer.Option(..., "--description", "-d"),
    file: str | None = typer.Option(None, "--file", "-f"),
) -> None:
    """Attach evidence (optionally a file, hashed on ingest) to a node."""
    p = _open(project)
    file_path, digest = None, None
    if file:
        new_path, digest = ingest_file(Path(project), Path(file))
        file_path = str(new_path)
    p.add_evidence(Evidence(node_id=node, description=description, file_path=file_path, sha256=digest))
    console.print(f"[green]Evidence recorded for[/green] {node}")


@app.command()
def graph(
    project: str = typer.Option(..., "--project", "-p"),
    out: str | None = typer.Option(None, "--out", help="Write Mermaid to this file instead of stdout."),
) -> None:
    """Render the current attack-path graph as Mermaid."""
    p = _open(project)
    text = render_mermaid(p)
    if out:
        Path(out).write_text(text)
        console.print(f"[green]Written:[/green] {out}")
    else:
        console.print(text)


@app.command()
def report(
    project: str = typer.Option(..., "--project", "-p"),
    out: str = typer.Option("report.md", "--out"),
) -> None:
    """Generate the engagement Markdown report."""
    p = _open(project)
    Path(out).write_text(build_report(p))
    console.print(f"[green]Report written:[/green] {out}")


@ai_app.command("advise")
def ai_advise(
    project: str = typer.Option(..., "--project", "-p"),
    node: str = typer.Option(..., "--node", "-n"),
    backend: str = typer.Option("ollama", "--backend", "-b", help="ollama|anthropic|openai|gemini"),
) -> None:
    """Ask an AI advisor for suggestions about one node, using only local data."""
    from siegegraph.ai.router import advise as run_advise

    p = _open(project)
    row = p.get_node(node)
    if not row:
        console.print(f"[red]No such node:[/red] {node}")
        raise typer.Exit(1)
    evidence = [dict(e) for e in p.list_evidence(node)]
    context = json.dumps({"node": dict(row), "evidence": evidence}, indent=2)
    template = (
        Path(__file__).parent / "ai" / "prompt_templates" / "triage.md"
    ).read_text()
    prompt = template.format(context=context)
    result = run_advise(p, backend, prompt, node_id=node)
    console.print(f"[bold]--- {result.provider} ---[/bold]")
    console.print(result.text)


if __name__ == "__main__":
    app()
