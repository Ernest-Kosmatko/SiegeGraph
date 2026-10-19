"""Render the engagement graph as a Mermaid flowchart for embedding in
Markdown reports or GitHub-rendered docs."""
from __future__ import annotations

from siegegraph.core.graph import Project

_SHAPE = {
    "host": ("[", "]"),
    "service": ("(", ")"),
    "vulnerability": ("{{", "}}"),
    "credential": ("([", "])"),
    "pivot": ("((", "))"),
    "objective": ("[[", "]]"),
}


def render(project: Project) -> str:
    lines = ["flowchart LR"]
    for row in project.list_nodes():
        left, right = _SHAPE.get(row["type"], ("[", "]"))
        safe_label = row["label"].replace('"', "'")
        lines.append(f'    {row["id"]}{left}"{safe_label}"{right}')
    for row in project.list_edges():
        label = row["type"].replace("_", " ")
        lines.append(f'    {row["source"]} -- "{label}" --> {row["target"]}')
    return "\n".join(lines)
