# Ask Acme

A permission-aware Retrieval-Augmented Generation (RAG) system that lets employees ask natural-language questions about internal documentation and receive grounded answers with citations — respecting per-document access controls.

> **Status:** Design phase. PRD complete; HLD in progress.
> **Project type:** Portfolio project demonstrating production-grade backend + AI engineering.

## What this is

Ask Acme is a fictional internal Q&A platform for a fictional warehouse robotics company (Acme Robotics). It exists to demonstrate, end-to-end, how to build a RAG system that is:

- **Permission-aware** — users only see answers grounded in documents they're authorized to read
- **Production-shaped** — designed with real concerns (latency, observability, evals, cost, audit logs) in mind
- **Documented like a real product** — full PRD, HLD, LLD, and Architecture Decision Records

The fictional framing exists so design choices can be discussed in the context of a real-feeling enterprise scenario, not as a generic toy.

## Repository structure

```
ask-acme/
├── docs/                    # Design documentation
│   ├── prd/                 # Product Requirements Document
│   ├── hld/                 # High-Level Design (with Mermaid diagrams)
│   ├── lld/                 # Low-Level Design
│   └── adr/                 # Architecture Decision Records
├── corpus/                  # Test corpus: fictional Acme Robotics docs
└── src/                     # Application source code (added in Phase 1)
```

## Documentation

- [Product Requirements Document](docs/prd/PRD.md) — what we're building and why
- [Documentation index](docs/README.md) — full list of design docs
- [Test corpus overview](corpus/README.md) — what the test data looks like

## Status

| Section | State |
|---|---|
| PRD | ✅ Complete |
| HLD | 🚧 In progress |
| LLD | ⏳ Not started |
| ADRs | ⏳ Not started |
| Phase 1 (Foundation) | ⏳ Not started |

## Why a portfolio project looks like this

This project is deliberately scoped and documented like a real production system rather than a tutorial. The goal is to demonstrate, by walking through it, how production backend engineers think about:

- Permission models in AI systems
- Retrieval evaluation and quality measurement
- LLM observability and cost control
- Honest scoping (what's in v1, what's deferred, why)

If you're reviewing this for a hiring decision, the PRD and ADRs are the best entry points.
