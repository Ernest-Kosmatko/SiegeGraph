from pathlib import Path

from siegegraph.core.graph import Project
from siegegraph.core.models import Edge, EdgeType, Engagement, Node, NodeType


def test_round_trip(tmp_path: Path) -> None:
    db = tmp_path / "demo.siege"
    p = Project(db)
    p.create_engagement(Engagement(name="Demo Co. Internal Pentest", client="Demo Co."))

    host = p.add_node(Node(type=NodeType.HOST, label="10.10.10.5"))
    svc = p.add_node(Node(type=NodeType.SERVICE, label="smb/445"))
    vuln = p.add_node(Node(type=NodeType.VULNERABILITY, label="MS17-010"))

    p.add_edge(Edge(source=host.id, target=svc.id, type=EdgeType.EXPOSES))
    p.add_edge(Edge(source=vuln.id, target=svc.id, type=EdgeType.AFFECTS))

    assert len(p.list_nodes()) == 3
    assert len(p.list_edges()) == 2

    g = p.to_networkx()
    assert g.number_of_nodes() == 3
    p.close()


def test_kill_chain_paths(tmp_path: Path) -> None:
    db = tmp_path / "demo2.siege"
    p = Project(db)
    p.create_engagement(Engagement(name="Chain test"))

    host = p.add_node(Node(type=NodeType.HOST, label="dc01"))
    cred = p.add_node(Node(type=NodeType.CREDENTIAL, label="domain admin hash"))
    objective = p.add_node(Node(type=NodeType.OBJECTIVE, label="Domain Admin"))

    p.add_edge(Edge(source=host.id, target=cred.id, type=EdgeType.YIELDS))
    p.add_edge(Edge(source=cred.id, target=objective.id, type=EdgeType.GRANTS_ACCESS_TO))

    paths = p.kill_chain_paths(NodeType.HOST, NodeType.OBJECTIVE)
    assert len(paths) == 1
    assert paths[0] == [host.id, cred.id, objective.id]
    p.close()
