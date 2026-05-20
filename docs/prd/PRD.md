# Ask Acme — Product Requirements Document

**Status:** Locked
**Author:** Sanjoli Sirohi, Platform Engineering
**Last Updated:** _[date]_

---

## 1. Overview

Ask Acme is an internal Q&A platform that lets any Acme Robotics employee ask natural-language questions about company knowledge — engineering runbooks, HR policies, product documentation, customer FAQs — and receive grounded answers with citations to source documents. The system respects existing document permissions: a user only sees answers derived from documents they are authorized to read.

## 2. Problem Statement

Acme's institutional knowledge is fragmented across multiple systems: Notion (product docs), Google Drive (HR and finance), GitHub wikis (engineering), and Confluence (legacy runbooks). Four problems result from this fragmentation:

1. **New hires spend their first 2-3 weeks searching for basic information** that already exists somewhere in the company. Onboarding surveys consistently rank "finding things" as the top frustration.

2. **Subject matter experts spend significant time answering the same questions repeatedly.** Senior engineers report 4-6 hours per week answering questions whose answers already exist in documentation. HR Business Partners spend an estimated 30% of their time on routine policy questions.

3. **Existing search tools return links, not answers.** Employees who find the right document still have to read through it to extract what they need. For policy questions, this introduces interpretation risk — employees may misread a policy and act on the wrong conclusion.

4. **Any solution must respect existing document permissions.** Engineering runbooks are visible to engineers and product teams but not to finance. HR compensation bands are restricted to HR Business Partners. Finance board updates are executive-only. A system that surfaces information users aren't authorized to see is a compliance failure — not just a UX inconvenience.

## 3. User Personas

Ask Acme has three user personas. Every user is exactly one of these types. A user's persona is independent of their content-group membership — an Admin in the `hr` group can configure the system and see HR documents; a Regular User in the `hr` group can see HR documents but cannot configure the system.

### 3.1 Admin (Platform / IT Engineer)

**Who:** Members of the Platform Engineering or IT team responsible for operating Ask Acme. Expected headcount: 2-4 people during initial rollout.

**What they do:**
- Configure source connectors (Notion workspace, Google Drive folder, GitHub repos) and the credentials each connector uses
- Define content groups and the rules that assign documents to those groups
- Manage user accounts: create accounts, assign personas, assign content-group memberships, deactivate accounts
- Monitor system health: query volume, retrieval latency, LLM cost per day, eval scores over time
- Trigger and observe ingestion runs; investigate failed documents

**What they don't do:**
- Modify document content (Ask Acme is read-only on source data)
- Override permission decisions for individual queries
- Write or modify prompts (prompt updates are code changes, not config)

**Approximate user count at launch:** 4

### 3.2 Regular User (Employee)

**Who:** Any Acme Robotics employee who has completed onboarding. The default persona; the system is built primarily for them.

**What they do:**
- Ask natural-language questions via the `/ask` API or web UI
- Receive answers with inline citations linking to source documents
- See only chunks from documents their content groups authorize
- Provide feedback on answers (thumbs up / thumbs down + optional comment)
- View their own query history (last 30 days)
- Export a query and its answer (for sharing in Slack, for example)

**What they don't do:**
- See other users' queries or query history
- Configure the system in any way
- Modify their own content-group memberships
- Bypass permission filtering

**Approximate user count at launch:** ~800

### 3.3 Viewer (Limited Access)

**Who:** New hires in their first two weeks, external auditors with temporary access, or contractors with limited engagement. Membership in `public` content group only by default.

**What they do:**
- Ask questions and receive answers from public documents only
- See citations for the documents they're authorized to view

**What they don't do:**
- Provide feedback (no thumbs up/down)
- Save query history (queries are not persisted past the session)
- Access non-public content even if their question implicitly references it
- Self-upgrade to Regular User

**Approximate user count at launch:** ~50 (rotating)

### 3.4 Content Groups

Permissions are modeled as **flat groups with team-level granularity**. A user belongs to one or more groups; a document is tagged with one or more groups. A user can see a chunk if and only if at least one of their groups matches at least one tag on that chunk's source document.

Initial content groups at launch:

| Group | Purpose | Example documents |
|---|---|---|
| `public` | Visible to all employees including Viewers | Company overview, careers page, customer stories, public blog posts |
| `eng-shared` | Cross-engineering knowledge | Coding standards, on-call rotations, postmortems affecting multiple teams |
| `eng-platform` | Platform Infrastructure team | Fleet Manager architecture, telemetry runbooks, migration docs |
| `eng-path-planner` | Path Planner team | Path-planner internal designs, perf-tuning notes |
| `eng-fleet-ui` | Fleet UI team | UI design docs, frontend onboarding |
| `product` | Product Management | Roadmaps, competitive analyses, customer FAQs, integration guides |
| `hr` | All HR | General HR policies (PTO, onboarding, reviews) |
| `hr-business-partners` | HR Business Partners only | Compensation bands, individual employee data |
| `finance` | Finance team | Expense policy, vendor lists, procurement |
| `finance-exec` | Finance leadership and executive staff | Board updates, M&A memos, runway analysis |

Users typically belong to 2-4 groups: their team-level group, the cross-functional group for their function (e.g., `eng-shared` for any engineer), and `public`. Group membership is managed manually by Admins through the admin API. Automatic synchronization from an HR system of record is out of scope for the initial release (see Section 9).

### 3.5 Considered Alternatives for Permission Modeling

We considered three permission models:

- **Flat groups (chosen):** Simplest to implement, test, and reason about. Sufficient for our scale of ~10 groups and ~850 users.
- **Hierarchical groups (RBAC tree):** Groups inherit from parent groups. More natural for large orgs but doubles implementation complexity and makes auditing harder.
- **Attribute-based access control (ABAC):** Permissions expressed as policies over user/document attributes. Most flexible, also most operationally expensive.

We chose flat groups for the initial implementation. If Acme scales past ~100 groups or needs automatic org-rollup permissions, the data model is designed to migrate to a tree structure without changing the on-disk schema. ABAC is not currently planned.

## 4. Functional Requirements

Each requirement is numbered and assigned a priority:

- **P0** — Must be in v1. The system is not functional without it.
- **P1** — Should be in v1 if possible. The system works without it but is significantly less useful.
- **P2** — Nice to have. Deferred to a future release unless time permits.

Every FR has a **testability note** indicating how the requirement is verified.

### 4.1 Ingestion

**FR-1 (P0):** The system shall ingest documents from a configured source location. For v1, the source is a local directory of markdown files. The connector interface is designed for extension; additional connectors are added in later releases.
*Testability:* Run ingestion against the test corpus; verify all 26 documents appear in storage.

**FR-2 (P0):** The system shall chunk each document into smaller segments suitable for embedding and retrieval. Chunks are token-bounded (target ~500 tokens per chunk, configurable) with overlap (target ~50 tokens, configurable) to preserve cross-boundary context.
*Testability:* Ingest a known document; verify the chunk count and that consecutive chunks share overlap text.

**FR-3 (P0):** The system shall generate a vector embedding for each chunk using an external embedding model. The embedding model is configurable. Default for v1 is OpenAI's `text-embedding-3-small`.
*Testability:* After ingestion, verify the chunk count equals the embedding count in the vector store; spot-check that embeddings have the expected dimensionality.

**FR-4 (P0):** The system shall tag each chunk with the content groups its source document belongs to. Tags are derived from a configurable mapping rule. In v1, the rule maps source folder path to content groups.
*Testability:* Ingest the corpus; verify that every chunk has at least one content group tag, and that no chunk in `corpus/public/` carries a non-public tag.

**FR-5 (P0):** Ingestion shall be idempotent. Re-ingesting the same source content shall not create duplicate chunks. Detection is based on a content hash of each source document.
*Testability:* Run ingestion twice on the same corpus; verify the second run reports zero new chunks created.

**FR-6 (P1):** The system shall report ingestion progress and errors. For each ingestion run, the system records: total documents found, documents successfully chunked, documents failed (with reasons), total chunks created, total embeddings generated, elapsed time, and total embedding API cost.
*Testability:* Run ingestion with an intentionally malformed document; verify the failure is recorded with a clear reason.

**FR-7 (P2):** The system shall support incremental ingestion. When a document changes in the source, only that document is re-chunked and re-embedded; unchanged documents are skipped.
*Note: Deferred to Phase 4 when real connectors are added.*

### 4.2 Retrieval & Search

**FR-8 (P0):** The system shall retrieve the top-K chunks most semantically similar to a query. K is configurable per request, with a default of 5 and a maximum of 20.
*Testability:* Submit a query that should match a specific chunk in the corpus; verify that chunk appears in the top-5 results.

**FR-9 (P0):** The system shall combine vector similarity and keyword search ("hybrid search"). Final ranking is produced by fusing vector and keyword rankings using Reciprocal Rank Fusion (RRF) or an equivalent technique.
*Testability:* For a query containing a unique identifier (e.g., "TD-118"), verify the chunk containing that identifier appears in the top-3 hybrid results even when its semantic similarity is low.

**FR-10 (P1):** The system shall apply a reranking stage after initial retrieval. A reranker model receives the top-N candidates from hybrid search (N > K) and produces a final top-K ranking.
*Testability:* Compare top-5 precision on a labeled query set with and without reranking; verify reranking produces equal or better precision.

**FR-11 (P0):** Retrieval shall enforce content-group permissions at query time. A chunk shall be returned only if at least one of the asking user's content groups matches at least one of the chunk's tags.
*Testability:* Submit a query as a Viewer user that targets HR content; verify zero chunks from the `hr` or `hr-business-partners` groups appear in results.

**FR-12 (P0):** Permission filtering shall not allow leakage through over-fetch. Permission filtering is applied *before* or *within* the vector search, not as a post-processing step that operates on already-retrieved unfiltered results.
*Testability:* Trace logs of a permission-restricted query; verify that no chunk from a restricted group is ever loaded into application memory.

### 4.3 Query & Answer Generation

**FR-13 (P0):** The system shall accept a natural-language query and return a generated answer with citations. The query is a single-turn question (no conversation history). The response includes the generated answer text and a list of source chunks used.
*Testability:* Submit a question with a known answer in the corpus; verify the response contains the correct answer and a citation to the source chunk.

**FR-14 (P0):** Generated answers shall be grounded in retrieved chunks. The LLM is instructed to answer using only the provided context. If no retrieved chunks are relevant to the query, the system shall return a response indicating that no relevant information was found rather than generating an unsupported answer.
*Testability:* Submit a question with no answer in the corpus; verify the response indicates no answer is available, rather than fabricating one.

**FR-15 (P0):** Each answer shall include citations to the chunks that support it. A citation includes at minimum: source document identifier, chunk index, and a short excerpt that supports the cited claim.
*Testability:* For an answered question, verify that following each citation back to its source chunk reveals text that supports the cited claim.

**FR-16 (P1):** Citations shall be inline within the answer, not only at the end. Each claim in the answer is followed by a marker (e.g., `[1]`, `[2]`) corresponding to a specific citation.
*Testability:* Submit a multi-claim question; verify each claim has its own citation marker.

**FR-17 (P0):** The LLM provider shall be configurable. The system can switch between supported providers (OpenAI, Anthropic) without code changes, via configuration.
*Testability:* Switch the configured provider; verify queries succeed against the new provider without redeploying.

### 4.4 Permissions

**FR-18 (P0):** Every query shall be associated with an authenticated user identity. Unauthenticated queries are rejected with HTTP 401.
*Testability:* Submit a query without an auth token; verify a 401 response.

**FR-19 (P0):** A user belongs to one persona and zero or more content groups. Persona and group memberships are stored separately. A user with no content groups can submit queries but will receive no results from any non-public content.
*Testability:* Create a user with no content groups; submit a query; verify the response includes only chunks from the `public` group.

**FR-20 (P0):** Content groups are flat, not hierarchical. A user can belong to any number of content groups. Membership in one group does not imply membership in any other group. New Regular Users and Admins are assigned the `public` group by default; Viewers are assigned only the `public` group. All other group memberships are explicitly assigned by an Admin (FR-23).
*Testability:* Create a user with groups `{public, eng-platform}`. Submit a query whose answer is in an `eng-shared` document; verify the chunk is NOT returned. Submit the same query against an `eng-platform` document; verify the chunk IS returned. This confirms that `eng-platform` membership does not implicitly grant `eng-shared` access.

**FR-21 (P0):** Audit logs shall record every query and the groups used to authorize it. Each query produces a log record containing: user ID, persona, content groups at query time, query text, retrieved chunk IDs, and timestamp. Logs are retained for 90 days.
*Testability:* Submit a query; verify the audit log contains all required fields within 5 seconds.

### 4.5 Admin & Configuration

**FR-22 (P0):** An Admin can create, modify, and deactivate user accounts. User attributes managed by Admin: email, persona, content groups, status (active/deactivated).
*Testability:* As an Admin, create a user; verify the user can log in and submit queries.

**FR-23 (P0):** An Admin can assign and revoke content-group memberships for any user. Membership changes take effect on the user's next query (no caching of permissions across requests).
*Testability:* Add a group to a user, immediately submit a query as that user; verify the new group's content is now accessible.

**FR-24 (P1):** An Admin can view system health metrics. Metrics surfaced: query volume per day, retrieval latency p50/p95/p99, LLM cost per day, ingestion run history, and most recent eval scores.
*Testability:* As an Admin, fetch the metrics endpoint; verify all expected metrics are present and non-null.

**FR-25 (P1):** An Admin can trigger an ingestion run on demand. On-demand runs are an override for the scheduled ingestion (FR-30), used after large content updates when waiting for the next scheduled run is undesirable.
*Testability:* As an Admin, trigger an ingestion run; verify the run starts and produces the expected log output.

### 4.6 Feedback & Observability

**FR-26 (P1):** Regular Users can submit feedback on each answer (thumbs up / thumbs down + optional comment). Feedback is persisted with the query record and is visible to Admins for review.
*Testability:* Submit feedback on a query; verify it appears in the query record and in the Admin feedback dashboard.

**FR-27 (P0):** Every query, retrieval, and generation step shall be logged with structured fields suitable for analysis. Required fields: trace ID, user ID, query text, retrieved chunk IDs and similarity scores, LLM latency, LLM cost in tokens, total end-to-end latency.
*Testability:* Submit a query; verify all required fields appear in the structured log within 5 seconds.

**FR-28 (P1):** The system shall expose a metrics endpoint compatible with Prometheus scraping. Required metrics: `queries_total{persona, status}`, `query_latency_seconds{stage}`, `retrieval_chunks_returned`, `llm_cost_usd_total{provider}`, `ingestion_documents_processed_total{status}`.
*Testability:* `curl /metrics`; verify all expected metric names are present.

**FR-29 (P1):** The system shall run an automated evaluation suite on a schedule. A set of labeled query/answer pairs is evaluated against the running system. Metrics produced: retrieval precision@5, answer correctness (LLM-as-judge), citation accuracy.
*Testability:* Trigger an eval run; verify scores are computed and persisted with a timestamp.

### 4.7 Ingestion Scheduling and Rate Limiting

**FR-30 (P0):** The system shall run ingestion on a configurable schedule. Default schedule is every 30 minutes. Each run scans the configured source location for new or changed documents. For v1, all detected documents are processed (incremental support is FR-7, P2).
*Testability:* Configure a short schedule (e.g., every 60 seconds for testing); add a new document to the source location; verify it appears in retrieval results within 90 seconds.

**FR-31 (P1):** The system shall enforce a per-user rate limit on query requests. The default limit is 30 queries per minute per user, configurable by an Admin. Requests exceeding the limit are rejected with HTTP 429 and a `Retry-After` header. Rate limits apply to all personas equally.
*Testability:* Submit 31 queries in under a minute as the same user; verify the 31st is rejected with HTTP 429.

## 5. Non-Functional Requirements

Each NFR is labeled as either:

- **[Target]** — measured and validated as part of project completion
- **[Stated]** — what a real production system would commit to; not all are validated in this implementation

### 5.1 Performance

**NFR-1 [Target]: End-to-end query latency.** P50 < 3 seconds, P95 < 6 seconds, P99 < 10 seconds, measured from when the `/ask` endpoint receives a request to when it returns the response. Includes retrieval, reranking, and LLM generation.

**NFR-2 [Target]: Retrieval latency.** P95 < 500ms, measured from the moment the retrieval module is called to when ranked chunks are returned. Excludes embedding API time for the query and LLM time.

**NFR-3 [Target]: Ingestion throughput.** The system shall ingest at least 100 documents per minute on a single ingestion worker, including chunking, embedding API calls (batched), and storage.

**NFR-4 [Stated]: Concurrent queries.** The system shall support 5 concurrent queries per second sustained, with the ability to burst to 20 QPS.

### 5.2 Scalability

**NFR-5 [Stated]: Corpus size.** The system shall handle up to 100,000 chunks in the vector store without architectural change.

**NFR-6 [Stated]: User scale.** The system shall support up to 2,000 active users without architectural change.

**NFR-7 [Stated]: Cost scalability.** Per-query cost (embeddings + LLM) shall remain under $0.05 at the configured default models.

### 5.3 Reliability & Availability

**NFR-8 [Stated]: API availability.** 99.5% per month, measured at the `/ask` endpoint. Excludes scheduled maintenance windows.

**NFR-9 [Target]: LLM failure handling.** If the configured LLM provider returns an error or times out (configurable, default 30 seconds), the system shall retry once with exponential backoff; if retry fails, return HTTP 503 with a clear error message; log the failure with the trace ID. The system shall NOT silently fall back to a different model or return a fabricated answer.

**NFR-10 [Target]: Embedding API failure handling.** Same retry/fail semantics as NFR-9, applied to the embedding API used during ingestion. Failed documents are flagged in the ingestion report; the next ingestion run retries them.

**NFR-11 [Stated]: Data durability.** Within the v1 single-host deployment, durability is ensured by underlying database write-ahead logging and regular volume snapshots. Replication for cross-node failure resilience is out of scope for v1.

### 5.4 Security & Privacy

**NFR-12 [Target]: Authentication.** Every API request shall be authenticated. v1 supports bearer-token authentication with tokens issued by an Admin. Token validation is performed on every request (no caching beyond the request scope).

**NFR-13 [Target]: Authorization.** Every retrieval request shall verify the user's current content groups against chunk tags. No caching of permission decisions across requests.

**NFR-14 [Stated]: Data at rest.** All persistent data shall use encryption at rest provided by the underlying storage layer.

**NFR-15 [Stated]: Data in transit.** All external API calls (embedding, LLM, connectors) shall use TLS 1.2 or higher.

**NFR-16 [Target]: Query log retention.** Query logs are retained for 90 days, then automatically deleted. Feedback records are retained for 1 year.

**NFR-17 [Target]: No content leakage in error messages.** Error responses shall not include chunk content, internal IDs, or document metadata.

### 5.5 Observability

**NFR-18 [Target]: Structured logging.** Every request, retrieval, embedding call, and LLM call produces a structured log line (JSON) including: trace ID, user ID, latency, status, cost (where applicable), and error class if failed.

**NFR-19 [Target]: Distributed tracing.** All service-to-service calls within the system shall be traceable via a single trace ID across the request path. OpenTelemetry-compatible.

**NFR-20 [Target]: Metrics exposure.** A Prometheus-compatible metrics endpoint exposes all metrics specified in FR-28.

**NFR-21 [Stated]: Cost tracking.** Every query records its embedding cost and LLM cost. Aggregated cost per user, per day, and per persona shall be queryable.

### 5.6 Maintainability

**NFR-22 [Target]: Configuration over code.** All deployment-specific values shall be configurable via environment variables or config files, with no code changes required.

**NFR-23 [Target]: Local development.** The full system shall be runnable locally on a developer laptop via `docker-compose up`, with no external dependencies other than API credentials for embedding and LLM providers.

**NFR-24 [Target]: Test coverage.** Critical paths shall have integration test coverage. Pure unit test coverage target is 70% on changed code, enforced by CI.

## 6. Use Cases

### UC-1: Engineer Queries Engineering Documentation

**Actor:** Felix Tran, Senior Engineer on the Platform Infrastructure team
**Persona:** Regular User
**Content Groups:** `public`, `eng-shared`, `eng-platform`

**Preconditions:**
- Felix has an active user account with a valid bearer token
- The corpus has been ingested and indexed
- The Fleet Manager architecture document is in the corpus, tagged with `eng-platform`

**Main Flow:**

1. Felix sends a query: *"What language is the dispatch-service written in?"* (FR-13)
2. The system authenticates the request and resolves Felix's user identity, persona, and content groups (FR-18, FR-19).
3. The system performs a permission-filtered hybrid search and returns the top-K chunks Felix is authorized to see (FR-8, FR-9, FR-10, FR-11, FR-12).
4. The retrieved chunks include a passage from `fleet_manager_architecture.md`: *"dispatch-service — Assigns pick tasks to specific robots based on location, battery state, and current load. Written in Rust for low-latency scheduling."*
5. The system generates an answer grounded in the retrieved chunks, with inline citations (FR-13, FR-14, FR-15, FR-16).
6. The system returns the answer to Felix: *"The dispatch-service is written in Rust. It was chosen for its low-latency scheduling characteristics. [1]"*
7. The full request is logged with trace ID, user identity, retrieved chunk IDs, latencies, and costs (FR-21, FR-27).

**Postconditions:**
- Felix has received an answer with at least one verifiable citation
- An audit log entry exists capturing Felix's content groups at query time
- Cost and latency metrics for this query are reflected in system metrics
- Felix can optionally submit feedback on the answer (FR-26)

**Alternate Flow A — No matching chunks within Felix's content groups:** Follows UC-4 (no relevant information).

**Alternate Flow B — External AI service failure:** If the service fails after one retry, the system returns HTTP 503 with a clear error message; failure logged with trace ID (NFR-9, NFR-10).

**Alternate Flow C — Bearer token invalid or expired:** System returns HTTP 401 and logs the request without performing retrieval (FR-18).

**Alternate Flow D — Rate limit exceeded:** System returns HTTP 429 with `Retry-After` header (FR-31).

**FRs Exercised:** FR-8, FR-9, FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-18, FR-19, FR-21, FR-26, FR-27, FR-31
**NFRs Exercised:** NFR-1, NFR-2, NFR-9, NFR-10, NFR-12, NFR-13, NFR-17, NFR-18, NFR-19

### UC-2: Contractor with Limited Access Asks About Compensation

**Actor:** Aisha Patel, contractor with the Path Planner team for a 90-day engagement
**Persona:** Viewer
**Content Groups:** `public`

**Preconditions:**
- Aisha has an active Viewer account with a valid bearer token
- The corpus has been ingested; HR compensation bands tagged with `hr-business-partners`

**Main Flow:**

1. Aisha sends a query: *"What are the salary bands for senior engineers at Acme?"* (FR-13)
2. The system authenticates and resolves Aisha's identity, persona, and content groups (FR-18, FR-19).
3. The system performs a permission-filtered hybrid search. Chunks tagged with `hr-business-partners` are excluded because Aisha is not a member of that group (FR-11, FR-12).
4. No remaining chunks in Aisha's authorized scope contain compensation information.
5. The system generates a response indicating no relevant information is available (FR-14).
6. The system returns: *"I don't have information available to answer that question."* No citations.
7. The full request is logged (FR-21, FR-27).

**Postconditions:**
- Aisha has received a graceful "no information" response
- No content from `hr-business-partners` was loaded into application memory or generation context
- Audit log captures the request

**Alternate Flow A — Adversarial reframing:** If Aisha submits a follow-up query attempting to extract the same information through different phrasing, the same flow applies. Permission filtering is enforced before generation, not at the prompt level.

**Alternate Flow B — Viewer asks a public-scope question:** Follows UC-1's flow normally, returning a grounded answer from public documents.

**FRs Exercised:** FR-11, FR-12, FR-13, FR-14, FR-18, FR-19, FR-21, FR-27
**NFRs Exercised:** NFR-12, NFR-13, NFR-17

### UC-3: Admin Configures and Triggers Initial Ingestion

**Actor:** Diana Schmidt, Platform Engineer (Admin)
**Persona:** Admin
**Content Groups:** `public`, `eng-shared`, `eng-platform`

**Preconditions:**
- Diana has an active Admin account
- The Acme corpus directory is accessible to the ingestion worker
- No documents have been ingested yet

**Main Flow:**

1. Diana configures a new ingestion source pointing to the corpus directory, with a mapping rule deriving content-group tags from folder names (FR-1, FR-4).
2. The system validates the configuration.
3. Diana triggers an on-demand ingestion run (FR-25).
4. The system scans the source directory and identifies all documents.
5. For each document, the system extracts text, splits into token-bounded chunks with overlap, generates embeddings, and stores chunks with content-group tags (FR-2, FR-3, FR-4).
6. A content hash is recorded per source document for idempotency (FR-5).
7. The system produces an ingestion report (FR-6).
8. Diana reviews the report and confirms all expected documents were ingested.

**Postconditions:**
- All documents in the corpus are indexed and queryable by users in appropriate groups
- The ingestion run is recorded in run history (FR-24)
- A subsequent identical ingestion run creates no duplicates (FR-5)

**Alternate Flow A — Some documents fail:** Failures are recorded with reasons; other documents continue to process; failed documents can be retried.

**Alternate Flow B — Embedding API unavailable:** Run is aborted, partial state preserved, failure logged for retry (NFR-10).

**Alternate Flow C — Re-ingestion of unchanged corpus:** Content hashes detect no changes; zero new chunks created (FR-5).

**FRs Exercised:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-24, FR-25, FR-30
**NFRs Exercised:** NFR-3, NFR-10, NFR-18

### UC-4: User Asks a Question Outside the Corpus's Knowledge

**Actor:** Felix Tran (as in UC-1)
**Persona:** Regular User
**Content Groups:** `public`, `eng-shared`, `eng-platform`

**Preconditions:**
- Felix has an active account
- The corpus has been ingested
- The corpus does not contain information answering Felix's question

**Main Flow:**

1. Felix sends a query unrelated to the corpus: *"Who is the CEO of SpaceX?"* (FR-13)
2. The system authenticates and resolves Felix's identity (FR-18, FR-19).
3. The system performs a permission-filtered hybrid search.
4. Retrieved chunks fall below the configured relevance threshold, or no chunks are returned.
5. The system generates a "no information" response (FR-14).
6. The system returns: *"I don't have information available to answer that question. Ask Acme answers questions based on internal Acme Robotics documentation only."*
7. The request is logged with the "no answer" outcome (FR-27).

**Postconditions:**
- Felix has received a clear "no information" response
- The LLM did NOT fabricate an answer from its training data (FR-14 upheld)
- Query logged as "no answer" — useful signal for what knowledge to add

**Alternate Flow A — Low-confidence chunks returned anyway:** The system applies the relevance threshold check at the generation step.

**Alternate Flow B — Borderline-relevant chunks:** LLM is instructed to respond with "I don't have specific information about that" rather than synthesize an unsupported answer. Enforced by system prompt.

**FRs Exercised:** FR-11, FR-13, FR-14, FR-18, FR-19, FR-27
**NFRs Exercised:** NFR-12, NFR-13, NFR-17

### UC-5: User's Content-Group Membership Changes During an Active Session

**Actor:** Felix Tran, being temporarily added to the Path Planner team
**Persona:** Regular User
**Content Groups (at start):** `public`, `eng-shared`, `eng-platform`

**Preconditions:**
- Felix has an active account
- Path-planner team documents are tagged with `eng-path-planner`

**Main Flow:**

1. Felix submits a query: *"What is the path planner team's perf-tuning approach?"*
2. The system resolves Felix's current content groups: `{public, eng-shared, eng-platform}`. `eng-path-planner` is not present.
3. Permission-filtered hybrid search returns no chunks from `eng-path-planner` (FR-11, FR-12).
4. The system responds that no relevant information is available.
5. An Admin updates Felix's content groups, adding `eng-path-planner` (FR-23).
6. Felix submits the same query again, using the same bearer token.
7. The system resolves Felix's current content groups: `{public, eng-shared, eng-platform, eng-path-planner}`. The new group is now present (NFR-13).
8. Permission-filtered hybrid search now returns path-planner chunks (FR-11).
9. The system generates a grounded answer with citations.
10. Felix receives the answer.

**Postconditions:**
- New group membership took effect on the next query, with no session refresh required (FR-23, NFR-13)
- Both queries are recorded in the audit log with the groups in effect at the time of each query (FR-21)

**Alternate Flow A — Permission revocation:** Same flow in reverse; the next query loses access to the removed group, regardless of session state.

**Alternate Flow B — Account deactivation:** System rejects all requests at authentication with HTTP 401 (FR-22).

**FRs Exercised:** FR-11, FR-18, FR-19, FR-21, FR-22, FR-23
**NFRs Exercised:** NFR-12, NFR-13, NFR-17

## 7. Success Metrics

Metrics are tagged as:
- **[Launch]** — measured for the initial launch decision
- **[30-day]** — measured 30 days post-launch
- **[Ongoing]** — measured continuously

### 7.1 Adoption

- **SM-1 [30-day]:** ≥ 20% of eligible Regular Users submit at least one query per week
- **SM-2 [30-day]:** Active users submit a median of ≥ 5 queries per week
- **SM-3 [Launch]:** A new user can submit their first successful query in under 5 minutes from account creation

### 7.2 Answer Quality

- **SM-4 [Launch]:** Retrieval precision@5 ≥ 0.75 on the labeled eval set
- **SM-5 [Launch]:** LLM-judged answer correctness ≥ 80% on the labeled eval set
- **SM-6 [Ongoing]:** Thumbs-up to thumbs-down ratio ≥ 4:1 across user feedback
- **SM-7 [Ongoing]:** Citation accuracy ≥ 90%, measured on a weekly sample of 20 queries

### 7.3 Permission Safety

- **SM-8 [Launch]:** Zero permission leaks across 50+ adversarial test queries
- **SM-9 [Ongoing]:** Zero permission-related incidents in production over the first 90 days

### 7.4 Cost

- **SM-10 [Ongoing]:** Median per-query cost (embedding + LLM) ≤ $0.05

## 8. Constraints & Assumptions

### 8.1 Constraints

**C-1: External AI dependencies.** The system depends on external commercial AI providers (OpenAI, Anthropic) for embeddings and LLM generation. Self-hosting open-source models is out of scope for v1.

**C-2: Single-host on-prem deployment for v1.** The system runs on a single on-premises host machine (or a developer workstation for the reference implementation). All services are co-located. Multi-host deployment, cloud deployment, multi-region availability, and disaster recovery are out of scope for v1 but are not architecturally precluded — services communicate over well-defined APIs and can be split across hosts when scale demands. On-premises deployment is the appropriate trust posture for handling sensitive internal content.

**C-3: English-only content.** All ingested documents and all queries are assumed to be in English.

**C-4: Markdown-only source format for v1.** Source documents are markdown files. Other formats are deferred.

**C-5: Read-only on source content.** Ask Acme does not modify source documents.

**C-6: No real-time content updates.** Document changes propagate at the cadence of scheduled ingestion (default 30 minutes).

### 8.2 Assumptions

**A-1: Source documents have meaningful permission tags.** The source system's existing permission structure provides enough information to derive content-group tags during ingestion.

**A-2: Users authenticate against an existing identity system.** Acme has a single sign-on system that issues bearer tokens. Ask Acme does not implement password management, account recovery, or MFA itself.

**A-3: Content is mostly textual.** Documents are predominantly text. Image-heavy, video, audio, or spreadsheet-dominated pages are not effectively searchable in v1.

**A-4: Per-query cost is acceptable.** The internal-tool budget can absorb the cost projected by SM-10.

**A-5: Users will provide feedback.** Phase 5's eval improvement loop depends on at least some users submitting feedback. If feedback rates fall below 5% of queries, the eval set must be expanded manually.

**A-6: LLM providers respect data-handling commitments.** Even though Ask Acme runs on-premises, queries are sent to external LLM providers for embedding generation and answer generation. We assume Acme has signed enterprise terms with the chosen provider that prohibit using customer data for training. On-prem deployment of the application alone does not provide complete data isolation; sensitive content still leaves the network for LLM inference. A fully air-gapped deployment would require self-hosted embedding and LLM models, which is out of scope for v1.

**A-7: HRIS integration is a future direction, not v1.** Manual group management is the v1 reality (per FR-23) but is not sustainable past ~1,000 users.

**A-8: Corpus growth is bounded.** Acme's corpus is expected to grow at ~10% per year. The NFR-5 ceiling of 100,000 chunks provides multi-year runway.

## 9. Out of Scope

The following capabilities are explicitly excluded from v1. Each is a deliberate scope decision, not an oversight.

### 9.1 AI / Retrieval Capabilities

- **Multi-turn conversation.** Each query is independent. Follow-up questions referencing prior turns are not supported.
- **Self-hosted (local) inference.** The system uses external commercial AI providers. Air-gapped or fully local deployment is supported via the provider abstraction (FR-17) but is not the v1 reference implementation.
- **Retrieval-only mode.** Every query produces a generated answer or a no-information response.
- **Multimodal content.** Images, diagrams, video, audio, and structured data are not extracted. Plain text only.
- **Fine-tuning or model customization.** Pre-trained models as provided by the vendor.

### 9.2 Operations & Infrastructure

- **Multi-host or multi-region deployment.** v1 runs on a single on-premises host.
- **Cross-host data replication.** Durability is handled by database write-ahead logging and volume snapshots only.
- **Backup and restore tooling.** Operationalized backup procedures are not built.
- **HRIS integration for group membership.** Manual management by Admins in v1.
- **Connector framework with real source systems.** v1 ingests from a local directory of markdown files only.

### 9.3 User Experience

- **Full web application.** v1 ships an API and a minimal HTML form. Polished UI deferred.
- **Mobile clients.** No iOS or Android applications.
- **Saved queries and collections.**
- **Sharing answers across users.**
- **Personalization.**

### 9.4 Compliance & Enterprise

- **Industry-specific compliance certifications.** SOC 2, HIPAA, ISO 27001, and similar are not pursued for v1.
- **Data residency controls.**
- **Granular audit reports.** Audit logs exist (FR-21) but no canned reporting tooling.
- **Multi-tenant isolation.** v1 serves a single organization.

### 9.5 Future Considerations

The following are *not* committed to but are likely directions for future versions if v1 is successful:

- Real connectors (Notion, Drive, GitHub)
- HRIS integration for automatic group sync
- Multi-turn conversation
- Self-hosted model option for security-sensitive deployments
- A real web UI
- Per-team analytics dashboards
