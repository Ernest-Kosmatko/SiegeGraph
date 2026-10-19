"""Data model for an engagement graph.

A SiegeGraph project represents one authorized engagement. Everything in
this module is a plain, serializable record - no network or process side
effects live here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class NodeType(str, Enum):
    HOST = "host"
    SERVICE = "service"
    VULNERABILITY = "vulnerability"
    CREDENTIAL = "credential"
    PIVOT = "pivot"
    OBJECTIVE = "objective"


class EdgeType(str, Enum):
    EXPOSES = "exposes"          # host -> service
    AFFECTS = "affects"          # vulnerability -> service/host
    EXPLOITS = "exploits"        # vulnerability -> leads to access
    LEADS_TO = "leads_to"        # generic kill-chain step
    GRANTS_ACCESS_TO = "grants_access_to"  # credential/pivot -> host
    YIELDS = "yields"            # exploitation -> credential


@dataclass
class Node:
    type: NodeType
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: "")
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = _new_id(self.type.value[:4])


@dataclass
class Edge:
    source: str
    target: str
    type: EdgeType
    note: str = ""
    id: str = field(default_factory=lambda: _new_id("edge"))
    created_at: str = field(default_factory=_now)


@dataclass
class Evidence:
    node_id: str
    description: str
    file_path: str | None = None
    sha256: str | None = None
    id: str = field(default_factory=lambda: _new_id("ev"))
    created_at: str = field(default_factory=_now)


@dataclass
class Engagement:
    name: str
    client: str = ""
    authorized_by: str = ""
    scope_note: str = ""
    id: str = field(default_factory=lambda: _new_id("eng"))
    created_at: str = field(default_factory=_now)
