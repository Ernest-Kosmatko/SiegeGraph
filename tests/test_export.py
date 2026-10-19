from pathlib import Path

from siegegraph.core.graph import Project
from siegegraph.core.models import Engagement, Node, NodeType
from siegegraph.export.mermaid import render
from siegegraph.export.report import build


def test_mermaid_render(tmp_path: Path) -> None:
    p = Project(tmp_path / "x.siege")
    p.create_engagement(Engagement(name="X"))
    p.add_node(Node(type=NodeType.HOST, label="target-01"))
    out = render(p)
    assert "flowchart LR" in out
    assert "target-01" in out
    p.close()


def test_report_build(tmp_path: Path) -> None:
    p = Project(tmp_path / "y.siege")
    p.create_engagement(Engagement(name="Y", client="Acme"))
    p.add_node(Node(type=NodeType.VULNERABILITY, label="SQLi in /login"))
    out = build(p)
    assert "Acme" in out
    assert "SQLi in /login" in out
    assert "Disclaimer" in out
    p.close()
