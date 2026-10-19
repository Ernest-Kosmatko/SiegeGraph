# Security Policy

## Scope

SiegeGraph is a local, offline-first engagement-management tool. It does
not expose a network service by default and does not transmit engagement
data anywhere unless you explicitly configure a cloud AI backend.

## Reporting a vulnerability

If you find a security issue in SiegeGraph itself (not in a system you
tested using it), please open a private security advisory on GitHub
rather than a public issue. Include steps to reproduce and the affected
version. We aim to acknowledge reports within 5 business days.

## Handling of engagement data

- `.siege` project files and the matching `.evidence/` directories contain
  client-confidential data. Do not commit them to version control; the
  default `.gitignore` already excludes them.
- `config/providers.yaml` may contain API key references. Do not commit
  it; use `config/providers.example.yaml` as the template.
- The `ai_log` table inside each project file is the authoritative record
  of what was sent to any third-party AI provider for that engagement.
