# Ask Acme — Documentation

This folder contains the design documentation for Ask Acme. Documents follow a deliberate progression: requirements (PRD) → high-level architecture (HLD) → low-level design (LLD) → decision records (ADRs).

## Status

| Document | State | Description |
|---|---|---|
| [PRD](prd/PRD.md) | ✅ Locked | Product spec: what we're building, for whom, with what requirements |
| [HLD](hld/HLD.md) | ✅ Locked | High-level architecture: system context, containers, data model, key flows, technology choices, cross-cutting concerns, open questions |
| [LLD](lld/LLD.md) | ⏳ Not started | Per-component detailed designs |
| [ADRs](adr/) | ⏳ Not started | Architecture Decision Records for technology choices |

## Where to start

For a new reader, the recommended reading order is:

1. **[PRD](prd/PRD.md)** — what we're building and why
2. **[HLD](hld/HLD.md)** — how the system is structured at a high level
3. **[Standalone diagrams](hld/diagrams/)** — each HLD diagram as a separate file, easy to edit individually
4. **[ADRs](adr/)** — the "why" behind specific decisions (forthcoming)

## Diagram index

All architecture diagrams live both inside [HLD.md](hld/HLD.md) and as standalone files in `hld/diagrams/` for easier editing:

| # | Diagram | File |
|---|---|---|
| 2 | System Context | [02_system_context.md](hld/diagrams/02_system_context.md) |
| 3a | Container Architecture (Static View) | [03a_container_static.md](hld/diagrams/03a_container_static.md) |
| 3b | Query Path (Dynamic View) | [03b_query_path.md](hld/diagrams/03b_query_path.md) |
| 3c | Ingestion Path (Dynamic View) | [03c_ingestion_path.md](hld/diagrams/03c_ingestion_path.md) |
| 4 | Postgres Data Model (ER) | [04_data_model.md](hld/diagrams/04_data_model.md) |
| 5.1 | Query Flow (Sequence) | [05_1_query_flow.md](hld/diagrams/05_1_query_flow.md) |
| 5.2 | Ingestion Flow (Sequence) | [05_2_ingestion_flow.md](hld/diagrams/05_2_ingestion_flow.md) |
| 5.3 | Permission Change Mid-Session (Sequence) | [05_3_permission_change.md](hld/diagrams/05_3_permission_change.md) |

All diagrams are written in Mermaid and render natively on GitHub.

## Document types

### Product Requirements Document (PRD)

Defines the product, who it serves, what it does, how we know it works, and what is not in scope.

### High-Level Design (HLD)

Architecture, components, data flow, infrastructure. Answers "how is this system shaped?"

### Low-Level Design (LLD)

Detailed designs of individual components: schemas, API contracts, key algorithms. Answers "how is each component built?"

### Architecture Decision Records (ADRs)

Short documents capturing significant design decisions and their reasoning. Each ADR is numbered (ADR-0001 onward) and follows the standard format: Context → Decision → Consequences.

## A note on docs as portfolio artifacts

These documents serve a dual purpose: they're a real design record for the project, and they're an interview artifact for backend / platform / AI infrastructure roles. Each doc is written to be defensible in a system design discussion — meaning every choice has a stated reason, and every requirement traces to a use case.
