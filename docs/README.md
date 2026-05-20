# Ask Acme — Documentation

This folder contains the design documentation for Ask Acme. Documents are organized by type and follow a deliberate progression: requirements (PRD) → high-level architecture (HLD) → low-level design (LLD) → decision records (ADRs).

## Where to start

For a new reader, the recommended reading order is:

1. **[PRD](prd/PRD.md)** — what we're building and why
2. **[HLD](hld/HLD.md)** — how the system is structured at a high level (architecture, components, data flow)
3. **[LLD](lld/LLD.md)** — detailed designs of individual components (schemas, APIs, algorithms)
4. **[ADRs](adr/)** — the "why" behind specific decisions

## Document types

### Product Requirements Document (PRD)

Defines the product, who it serves, what it does, how we know it works, and what is *not* in scope. The PRD is the contract between intent and implementation.

- [PRD.md](prd/PRD.md) — single source of truth for the product spec

### High-Level Design (HLD)

Describes the architecture: how the system is decomposed into components, how data flows, what infrastructure supports it. HLD answers "how is this system shaped?"

- [HLD.md](hld/HLD.md) — main architecture doc (in progress)
- [diagrams/](hld/diagrams/) — Mermaid sources for architecture, sequence, and data model diagrams

### Low-Level Design (LLD)

Describes the internals of individual components: data schemas, API contracts, key algorithms, configuration. LLD answers "how is each component built?"

- [LLD.md](lld/LLD.md) — main LLD doc (not started)

### Architecture Decision Records (ADRs)

Short documents capturing significant design decisions and the reasoning behind them. Each ADR is numbered (ADR-0001, ADR-0002, etc.) and follows the standard format: Context → Decision → Consequences.

- [adr/](adr/) — ADRs will appear here as design progresses

## A note on docs as portfolio artifacts

These documents serve a dual purpose: they're a real design record for the project, and they're an interview artifact for backend / platform / AI infrastructure roles. Each doc is written to be defensible in a system design discussion — meaning every choice has a stated reason, and every requirement traces to a use case.
