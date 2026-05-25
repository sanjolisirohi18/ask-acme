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

## Quick start

Clone the repo, set up `.env`, and bring the stack up with Docker Compose. Should take under 5 minutes on a machine with Docker already installed.

### Prerequisites

- **Docker** ≥ 24.0 with the Compose plugin (`docker compose`, not `docker-compose`)
- **Python** ≥ 3.10 (only needed if you want to run the app outside Docker — the containerized setup uses Python 3.12)
- **Git**
- An **OpenAI API key** with access to embeddings + chat models

Optional, for local development outside containers:
- `pip-tools` for managing dependencies

### Setup

1. **Clone the repository**

```bash
   git clone  ask-acme
   cd ask-acme
```

2. **Create your `.env` file**

```bash
   cp .env.example .env
```

   Then edit `.env` and fill in:
   - `POSTGRES_PASSWORD` — choose any value for local dev
   - `OPENAI_API_KEY` — your real OpenAI key (starts with `sk-...`)
   - Leave the other defaults as-is unless you have a reason to change them

3. **(Optional) Install dependencies locally**

   Only needed if you plan to run code outside Docker (tests, scripts, IDE integration):

```bash
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .                   # installs the `ask_acme` package itself
```

### Running

Bring up all three services (Qdrant, Postgres, app):

```bash
docker compose up -d
```

Watch them come up and reach `healthy` status:

```bash
docker compose ps
```

You should see something like:
NAME                  STATUS                    PORTS
ask-acme-app          Up (healthy)
ask-acme-postgres     Up (healthy)              0.0.0.0:5432->5432/tcp
ask-acme-qdrant       Up (healthy)              0.0.0.0:6333-6334->6333-6334/tcp

Follow logs from a specific service:

```bash
docker compose logs -f app
```

Stop everything (keeps volumes):

```bash
docker compose down
```

Stop and wipe all data (Postgres + Qdrant volumes):

```bash
docker compose down -v
```

### Verifying it works

**1. Postgres is reachable**

```bash
docker compose exec postgres psql -U acme -d acme -c "SELECT version();"
```

Should print the PostgreSQL 16 version banner.

**2. Qdrant is reachable**

```bash
curl http://localhost:6333/healthz
# → healthz check passed

curl http://localhost:6333/collections
# → {"result":{"collections":[]},"status":"ok","time":...}
```

You can also open the Qdrant dashboard in a browser: <http://localhost:6333/dashboard>

**3. The app container is alive**

For now the app is a placeholder (it just sleeps), so the smoke test is simply:

```bash
docker compose logs app
# → app placeholder running
```

Once a real FastAPI server is wired up, this section will be extended with:
- `curl http://localhost:8000/health` to hit the health endpoint
- A sample ingestion + query round-trip

**4. Config loads correctly**

If you installed the package locally, you can sanity-check that `pydantic-settings` reads your `.env`:

```bash
python -c "from ask_acme.config import settings; print(settings.qdrant_http_url, settings.postgres_host)"
# → http://qdrant:6333 postgres
```

> **Container vs host hostnames.** The `.env.example` defaults (`POSTGRES_HOST=postgres`, `QDRANT_HOST=qdrant`) assume the app runs *inside* the docker-compose network, where service names resolve as hostnames. If you want to run the app directly on your host machine against the containerized infra, override these in your `.env`:
>
> ```bash
> POSTGRES_HOST=localhost
> QDRANT_HOST=localhost
> ```
>
> The published ports (5432, 6333, 6334) are reachable from the host either way.

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
