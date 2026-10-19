-- One SiegeGraph project = one SQLite file = one engagement.
CREATE TABLE IF NOT EXISTS engagement (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT,
    authorized_by TEXT,
    scope_note TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS node (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    label TEXT NOT NULL,
    attributes TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS edge (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL REFERENCES node(id),
    target TEXT NOT NULL REFERENCES node(id),
    type TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL REFERENCES node(id),
    description TEXT NOT NULL,
    file_path TEXT,
    sha256 TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_log (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    node_id TEXT,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_edge_source ON edge(source);
CREATE INDEX IF NOT EXISTS idx_edge_target ON edge(target);
CREATE INDEX IF NOT EXISTS idx_evidence_node ON evidence(node_id);
