# Tech Debt Register

This document tracks known tech debt items across the platform. Items here are not necessarily urgent — they're items the team has explicitly decided to defer rather than address. The register is reviewed quarterly to decide which items to address.

## Critical (address within next quarter)

### TD-104: alerting service is a single point of failure

The alerting service runs as a single replica. If it crashes, we lose all incident notifications until it restarts. We've had this fail twice in 2024.

**Effort estimate:** 1 sprint
**Owner:** Marcus Yoon
**Quarter targeted:** Q4 2024

### TD-118: Postgres connection pool exhaustion under load

When fleet-api experiences a traffic spike, we hit connection pool limits before hitting CPU limits. This causes cascading failures into dispatch-service which shares the pool.

**Effort estimate:** 2 sprints
**Owner:** Felix Tran
**Quarter targeted:** Q1 2025

## Significant (address within 6 months)

### TD-91: telemetry-ingest doesn't validate schema versions

Telemetry messages from robots don't include a schema version field. When we evolve the telemetry schema, we have no clean way to handle robots running older firmware. We currently work around this with try/catch blocks at the consumer.

**Effort estimate:** 3 sprints (includes firmware change + consumer update)
**Owner:** Diana Schmidt (cloud), TBD (firmware)
**Quarter targeted:** Q2 2025

### TD-87: command-control WebSocket reconnects are not idempotent

When a robot reconnects, command-control sometimes re-sends commands the robot has already executed. We've mitigated this with client-side dedup in the firmware, but the server should handle it correctly.

**Effort estimate:** 2 sprints
**Owner:** Aisha Patel
**Quarter targeted:** Q1 2025

## Acknowledged (no current plan to fix)

### TD-66: path-planner uses a custom protobuf serializer

The path-planner uses a hand-written protobuf serializer (in C++) rather than the standard one because of perf concerns measured in 2022. The custom code is now 3 years old and the standard library has improved. We should benchmark and probably remove the custom code — but it's working and risk-averse to change.

### TD-22: monorepo build times are slow

A full clean build of the monorepo takes 47 minutes. Incremental builds are fast (under 90 seconds) so most engineers don't feel the pain, but it adds friction to CI. Adopting Bazel would help but the migration cost is high.

## Closed Items

For historical reference, items closed in 2024:

- TD-152: deprecated API v1 endpoints removed (Mar 2024)
- TD-78: replaced legacy authentication with OAuth 2.1 (Jun 2024)
- TD-141: migrated fleet-ui from Webpack to Vite (Aug 2024)
