# Ask Acme

A permission-aware Retrieval-Augmented Generation (RAG) system that lets employees ask natural-language questions about internal documentation and receive grounded answers with citations — respecting per-document access controls.

> **Status:** Phase 1 (Foundation) — in progress
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
├── src/
│   └── ask_acme/            # Python package
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Local dev orchestration
├── pyproject.toml           # Project metadata
├── requirements.in          # Top-level dependencies
└── requirements.txt         # Locked dependencies (generated)
```

## Status

| Section | State |
|---|---|
| PRD | ✅ Complete |
| HLD | ✅ Complete |
| LLD | ⏳ Not started (written incrementally during implementation) |
| ADRs | ⏳ Not started |
| Phase 1 (Foundation) | 🚧 In progress |

---

## Quick start

> _TODO: fill in once Phase 1 step 1 is complete. This section should let a reader clone the repo, set up environment, and run the system in under 5 minutes._

### Prerequisites

> _TODO: list versions of Docker, Python, etc._

### Setup

> _TODO: steps to clone, set up `.env`, build images._

### Running

> _TODO: `docker-compose up` instructions._

### Verifying it works

> _TODO: smoke tests, sample queries._

---

## Architecture

For a complete architectural overview, see the [HLD](docs/hld/HLD.md). At a high level:

- **API Service** (FastAPI) — handles HTTP requests, orchestrates retrieval and generation
- **Ingestion Worker** (Python) — processes documents on schedule or on-demand
- **Postgres** — relational source of truth (documents, chunks, users, audit logs)
- **Qdrant** — vector index over chunk embeddings

Phase 1 implements the API Service and Ingestion Worker as a single application. They split into separate processes in later phases.

## Environment variables

The system is configured via environment variables. Copy `.env.example` to `.env` and fill in values.

> _TODO: list of required env vars, populated during Step 1._

## Project commands

> _TODO: list of useful commands as they're built — ingest, search, run migrations, etc._

## Cost expectations

Embedding the full Acme corpus (~26 documents, ~150-200 chunks) costs approximately **$0.01-0.02** using OpenAI `text-embedding-3-small`. A single search query costs a fraction of a cent (embedding only; LLM generation is added in Phase 5).

Set a usage limit on your OpenAI account regardless — recommended cap is $10/month for development.

## Documentation

- [Product Requirements Document](docs/prd/PRD.md) — what we're building and why
- [High-Level Design](docs/hld/HLD.md) — architecture, components, data flow
- [Documentation index](docs/README.md) — full list of design docs
- [Test corpus overview](corpus/README.md) — what the test data looks like

## Development phases

The implementation is broken into 5 phases. Each phase builds on the previous.

| Phase | Scope | State |
|---|---|---|
| **Phase 1** | Foundation: ingestion pipeline, vector search, FastAPI skeleton | 🚧 In progress |
| **Phase 2** | Hybrid search (vector + BM25), reranking, retrieval evals | ⏳ |
| **Phase 3** | Permission model: users, content groups, query-time filtering, auth, rate limiting | ⏳ |
| **Phase 4** | Connector framework: real source systems beyond local filesystem | ⏳ |
| **Phase 5** | LLM generation with citations, end-to-end eval framework, observability | ⏳ |

## Why a portfolio project looks like this

This project is deliberately scoped and documented like a real production system rather than a tutorial. The goal is to demonstrate, by walking through it, how production backend engineers think about:

- Permission models in AI systems
- Retrieval evaluation and quality measurement
- LLM observability and cost control
- Honest scoping (what's in v1, what's deferred, why)

If you're reviewing this for a hiring decision, the [PRD](docs/prd/PRD.md) and [HLD](docs/hld/HLD.md) are the best entry points.

## License

MIT — see [LICENSE](LICENSE)
