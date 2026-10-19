"""Markdown report generation from a project's current state."""
from __future__ import annotations

from siegegraph.core.graph import Project
from siegegraph.export.mermaid import render as render_mermaid


def build(project: Project) -> str:
    eng = project.get_engagement()
    nodes = project.list_nodes()
    evidence = project.list_evidence()

    out = [f"# Engagement Report: {eng['name'] if eng else 'Untitled'}", ""]
    if eng:
        out += [
            f"- **Client:** {eng['client'] or '-'}",
            f"- **Authorized by:** {eng['authorized_by'] or '-'}",
            f"- **Scope:** {eng['scope_note'] or '-'}",
            "",
        ]

    out += ["## Attack Path", "", "```mermaid", render_mermaid(project), "```", ""]

    out += ["## Findings", ""]
    for n in nodes:
        if n["type"] != "vulnerability":
            continue
        out.append(f"### {n['label']} (`{n['id']}`)")
        node_evidence = [e for e in evidence if e["node_id"] == n["id"]]
        if node_evidence:
            out.append("")
            out.append("Evidence:")
            for e in node_evidence:
                out.append(f"- {e['description']}" + (f" (`{e['file_path']}`)" if e["file_path"] else ""))
        out.append("")

    out += [
        "## Disclaimer",
        "",
        "This report documents activity performed under written authorization "
        "as part of a scoped penetration testing engagement. Distribution is "
        "restricted to the client and authorized recipients.",
    ]
    return "\n".join(out)
