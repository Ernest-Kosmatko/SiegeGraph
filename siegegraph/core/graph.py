"""Project store: SQLite persistence + in-memory graph via networkx."""
from __future__ import annotations

import json
import sqlite3
from importlib import resources
from pathlib import Path

import networkx as nx

from siegegraph.core.models import Edge, EdgeType, Engagement, Evidence, Node, NodeType


class Project:
    """Opens (or creates) a single engagement file and exposes graph ops."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        is_new = not self.path.exists()
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        if is_new:
            self._init_schema()

    def _init_schema(self) -> None:
        schema = resources.files("siegegraph.db").joinpath("schema.sql").read_text()
        self.conn.executescript(schema)
        self.conn.commit()

    # -- engagement -----------------------------------------------------
    def create_engagement(self, eng: Engagement) -> None:
        self.conn.execute(
            "INSERT INTO engagement (id, name, client, authorized_by, scope_note, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (eng.id, eng.name, eng.client, eng.authorized_by, eng.scope_note, eng.created_at),
        )
        self.conn.commit()

    def get_engagement(self) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM engagement LIMIT 1").fetchone()

    # -- nodes ------------------------------------------------------------
    def add_node(self, node: Node) -> Node:
        self.conn.execute(
            "INSERT INTO node (id, type, label, attributes, created_at) VALUES (?, ?, ?, ?, ?)",
            (node.id, node.type.value, node.label, json.dumps(node.attributes), node.created_at),
        )
        self.conn.commit()
        return node

    def get_node(self, node_id: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM node WHERE id = ?", (node_id,)).fetchone()

    def list_nodes(self, type_filter: NodeType | None = None) -> list[sqlite3.Row]:
        if type_filter:
            return self.conn.execute(
                "SELECT * FROM node WHERE type = ? ORDER BY created_at", (type_filter.value,)
            ).fetchall()
        return self.conn.execute("SELECT * FROM node ORDER BY created_at").fetchall()

    # -- edges ------------------------------------------------------------
    def add_edge(self, edge: Edge) -> Edge:
        self.conn.execute(
            "INSERT INTO edge (id, source, target, type, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (edge.id, edge.source, edge.target, edge.type.value, edge.note, edge.created_at),
        )
        self.conn.commit()
        return edge

    def list_edges(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM edge ORDER BY created_at").fetchall()

    # -- evidence ----------------------------------------------------------
    def add_evidence(self, ev: Evidence) -> Evidence:
        self.conn.execute(
            "INSERT INTO evidence (id, node_id, description, file_path, sha256, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ev.id, ev.node_id, ev.description, ev.file_path, ev.sha256, ev.created_at),
        )
        self.conn.commit()
        return ev

    def list_evidence(self, node_id: str | None = None) -> list[sqlite3.Row]:
        if node_id:
            return self.conn.execute(
                "SELECT * FROM evidence WHERE node_id = ? ORDER BY created_at", (node_id,)
            ).fetchall()
        return self.conn.execute("SELECT * FROM evidence ORDER BY created_at").fetchall()

    # -- ai log --------------------------------------------------------------
    def log_ai_call(self, provider: str, node_id: str | None, prompt: str, response: str) -> None:
        from siegegraph.core.models import _new_id, _now

        self.conn.execute(
            "INSERT INTO ai_log (id, provider, node_id, prompt, response, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (_new_id("ai"), provider, node_id, prompt, response, _now()),
        )
        self.conn.commit()

    # -- graph view ------------------------------------------------------------
    def to_networkx(self) -> nx.DiGraph:
        g = nx.DiGraph()
        for row in self.list_nodes():
            g.add_node(row["id"], type=row["type"], label=row["label"])
        for row in self.list_edges():
            g.add_edge(row["source"], row["target"], type=row["type"], note=row["note"])
        return g

    def kill_chain_paths(self, start_type: NodeType, end_type: NodeType) -> list[list[str]]:
        """All simple paths from any node of start_type to any node of end_type."""
        g = self.to_networkx()
        starts = [n for n, d in g.nodes(data=True) if d.get("type") == start_type.value]
        ends = [n for n, d in g.nodes(data=True) if d.get("type") == end_type.value]
        paths: list[list[str]] = []
        for s in starts:
            for e in ends:
                paths.extend(nx.all_simple_paths(g, s, e))
        return paths

    def close(self) -> None:
        self.conn.close()
