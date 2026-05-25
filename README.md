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

`docker compose up` brings up the data stores (Qdrant + Postgres) plus an `app` container. **Heads-up for Phase 1:** the `app` container is currently a placeholder that just stays alive — the FastAPI service, ingestion, and search land in later Phase 1 steps. So today "running" means a healthy local Qdrant + Postgres you can build against.

### Prerequisites

- **Docker** + **Docker Compose v2** — runs the whole stack via `docker compose ...`.
- **Python 3.13+** — only for host-machine development/tooling (running code or `pip-compile` outside Docker); the containers ship their own interpreter.
- **An OpenAI API key** — required by config; used once the embedding/generation steps land. Set a low spend cap (see [Cost expectations](#cost-expectations)).

### Setup

```bash
git clone <repo-url> ask-acme && cd ask-acme

# 1. Configure: copy the template and fill in values.
cp .env.example .env
#    The only value you must change is OPENAI_API_KEY (the template ships a
#    placeholder). Everything else has a working local default — see the
#    Environment variables table below and src/ask_acme/config.py.

# 2. (Optional) Host-machine dev env, to run code/tooling outside Docker.
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # pinned runtime deps
pip install -e .                  # the ask_acme package itself (metadata only, no deps)
```

### Running

```bash
docker compose up -d           # start Qdrant (6333/6334), Postgres (5432), app
docker compose ps              # check service health
docker compose logs -f app     # follow the app container
docker compose down            # stop everything (add -v to also wipe data volumes)
```

Ports are published to `localhost`, so host-machine code uses the `config.py` defaults (`localhost:6333`, `localhost:5432`) with no overrides needed.

### Verifying it works

```bash
docker compose ps                                  # qdrant + postgres should report "(healthy)"
curl http://localhost:6333/collections             # Qdrant -> JSON like {"result":{"collections":[]},"status":"ok",...}
docker compose exec postgres psql -U acme -d acme -c '\conninfo'   # -> connected as user "acme" (use your POSTGRES_USER/DB if changed)
```

Open the Qdrant dashboard at <http://localhost:6333/dashboard> to confirm the vector store is reachable. End-to-end smoke tests and sample queries arrive with the ingestion/search steps later in Phase 1; LLM-generated answers come in Phase 5.

---

## Architecture

For a complete architectural overview, see the [HLD](docs/hld/HLD.md). At a high level:

- **API Service** (FastAPI) — handles HTTP requests, orchestrates retrieval and generation
- **Ingestion Worker** (Python) — processes documents on schedule or on-demand
- **Postgres** — relational source of truth (documents, chunks, users, audit logs)
- **Qdrant** — vector index over chunk embeddings

Phase 1 implements the API Service and Ingestion Worker as a single application. They split into separate processes in later phases.

> **Local dev security note:** the local Qdrant runs **unauthenticated** — no `QDRANT_API_KEY` is set on the container and its ports are published to `localhost`, so anything that can reach port 6333/6334 can read/write the index. This is acceptable for single-machine Phase 1 development only; production would enable an API key (`qdrant_api_key` is already wired in [config](src/ask_acme/config.py)), keep the data stores on a private network, and stop publishing their ports to the host. (Postgres is in the same boat: it uses a weak default password and a published port.)

## Environment variables

The system is configured via environment variables. Copy `.env.example` to `.env` and fill in values. The full schema (types, defaults, validation) lives in [`src/ask_acme/config.py`](src/ask_acme/config.py); a missing **required** variable makes the app fail fast at startup.

**Required** — no default; the app won't start without these (the `.env.example` template pre-fills working values for all but `OPENAI_API_KEY`):

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI key for embeddings (and, later, generation). Must be a real key. |
| `POSTGRES_USER` | Postgres username. Also consumed by the Postgres container on first boot. |
| `POSTGRES_PASSWORD` | Postgres password. Also consumed by the Postgres container on first boot. |
| `POSTGRES_DB` | Postgres database name. Also consumed by the Postgres container on first boot. |
| `QDRANT_COLLECTION` | Name of the Qdrant collection holding chunk embeddings. |

**Optional** — sensible defaults; override only when needed:

| Variable | Default | Notes |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | Compose overrides to `postgres` inside the network. |
| `POSTGRES_PORT` | `5432` | |
| `QDRANT_HOST` | `localhost` | Compose overrides to `qdrant` inside the network. |
| `QDRANT_HTTP_PORT` | `6333` | REST API + dashboard. |
| `QDRANT_GRPC_PORT` | `6334` | gRPC. |
| `QDRANT_API_KEY` | _(unset)_ | Local Qdrant is unauthenticated; set this when the server enforces a key. |
| `ASK_ACME_ENV` | `development` | `development` \| `staging` \| `production`. |
| `ASK_ACME_LOG_LEVEL` | `INFO` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR`. |
| `ASK_ACME_DEBUG` | `false` | |
| `ASK_ACME_HOST` | `0.0.0.0` | API server bind address (used once the server exists). |
| `ASK_ACME_PORT` | `8000` | API server port (used once the server exists). |

## Project commands

What exists today (Phase 1 scaffold):

```bash
# Stack
docker compose up -d            # start Qdrant + Postgres + app
docker compose down             # stop (add -v to also delete data volumes)
docker compose logs -f <svc>    # tail logs: svc = qdrant | postgres | app

# Dependencies (host-machine)
pip install -r requirements.txt # install pinned deps into your venv
pip-compile requirements.in     # regenerate requirements.txt after editing requirements.in
```

Ingest, search, and database-migration commands will be added here as their Phase 1 steps land.

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
