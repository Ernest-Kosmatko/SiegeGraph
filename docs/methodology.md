# Methodology & Data Model

## Why a graph

A penetration test produces facts faster than they can be structured:
a port here, a default credential there, a stale CVE on a forgotten
host. SiegeGraph's only job is to keep those facts connected as you add
them, so the path from initial access to objective is explicit rather
than reconstructed from memory at report time.

## Node types

| Type | Represents |
|---|---|
| `host` | A reachable system |
| `service` | A listening service on a host |
| `vulnerability` | A specific weakness affecting a service or host |
| `credential` | Something obtained during the engagement |
| `pivot` | A foothold used to reach further hosts |
| `objective` | A stated goal of the engagement (e.g. domain admin) |

## Edge types

`exposes`, `affects`, `exploits`, `leads_to`, `grants_access_to`, `yields`.
Edges are directional and timestamped; the graph is a record of what was
established and when, not a static topology diagram.

## Evidence

Each piece of evidence is tied to exactly one node and, if a file is
attached, hashed on ingest (SHA-256). The hash is stored next to the
description so a report can state that evidence has not been modified
since capture.

## AI advisor boundary

The advisor layer is deliberately read-only with respect to the graph: it
receives a snapshot of one node and its evidence, returns free text, and
never writes to the project file except through the `ai_log` audit table.
Adding a suggested node or edge is always a separate, explicit operator
action.
