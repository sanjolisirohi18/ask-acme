# Fleet Manager Architecture Overview

The Fleet Manager is Acme's cloud-hosted control plane that coordinates WX-7 robot fleets across customer warehouses. It consists of seven microservices communicating over gRPC, backed by a multi-region Postgres cluster and a Kafka event bus.

## Services

The Fleet Manager comprises the following services:

1. **fleet-api** — Public REST and gRPC API gateway. Handles authentication via OAuth 2.1 with JWT bearer tokens. Implemented in Go.
2. **dispatch-service** — Assigns pick tasks to specific robots based on location, battery state, and current load. Written in Rust for low-latency scheduling.
3. **telemetry-ingest** — Receives sensor telemetry from robots at approximately 80 Hz per robot. Streams data into Kafka topics partitioned by facility ID.
4. **path-planner** — Computes optimal navigation paths using a modified A* algorithm with dynamic obstacle avoidance. Written in C++ with Python bindings.
5. **command-control** — Issues motion commands to individual robots via a persistent WebSocket connection.
6. **fleet-ui** — React-based operator dashboard served via Next.js.
7. **alerting** — Anomaly detection and PagerDuty integration. Written in Python.

## Data Storage

Robot state is sharded across a Postgres cluster using Citus, partitioned by facility ID. Telemetry data lands in Kafka and is archived to S3 in Parquet format after 7 days for long-term analytics. Operational metrics are stored in Prometheus with a 30-day retention.

## Deployment

The Fleet Manager runs on Kubernetes (EKS) across three AWS regions: us-east-1, us-west-2, and eu-central-1. Each region is fully self-contained; cross-region replication uses a custom event-sourcing layer to maintain consistency. Deployments use Argo CD with progressive rollouts.

## SLOs

Our published service-level objectives:

- API availability: 99.95% per quarter
- Dispatch latency: p99 under 200ms
- Telemetry ingest: zero data loss within a 30-second window
