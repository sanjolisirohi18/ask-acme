# Design Doc: Migrating Telemetry Storage from Kafka to Redpanda

**Status:** Draft
**Author:** Diana Schmidt, Platform Infrastructure
**Reviewers:** Priya Vasquez, Marcus Yoon, Felix Tran

## Context

We currently use Apache Kafka (deployed via Strimzi on EKS) as the event bus for robot telemetry. As of August 2024, we ingest approximately 2.4 TB of telemetry data daily across the fleet. Our Kafka cluster runs on 12 brokers in each region with 3-way replication.

We are seeing increasing operational burden from Kafka: ZooKeeper coordination issues, slow rolling restarts, and difficulty hiring engineers familiar with Kafka tuning.

## Proposal

Migrate the telemetry pipeline from Kafka to Redpanda. Redpanda is API-compatible with Kafka, removes the ZooKeeper dependency, and has demonstrated lower tail latencies in our internal benchmarks.

## Benchmarks

We ran a 14-day load test comparing Kafka and Redpanda at 1.5x our production load:

| Metric | Kafka | Redpanda |
|---|---|---|
| Median producer latency | 8 ms | 4 ms |
| P99 producer latency | 142 ms | 38 ms |
| Median consumer lag during rolling restart | 4.2 s | 0.9 s |
| Operator-reported incidents over 14 days | 6 | 1 |

## Migration Plan

Phase 1 (Q4 2024): Stand up Redpanda in us-east-1 alongside existing Kafka. Mirror traffic via MirrorMaker 2 for validation.

Phase 2 (Q1 2025): Cut over `telemetry-ingest` consumers to read from Redpanda. Kafka remains running in standby.

Phase 3 (Q2 2025): Cut over producers. Decommission Kafka in us-east-1.

Phase 4 (Q3 2025): Roll out same migration to us-west-2 and eu-central-1.

## Risks

- Compatibility edge cases in MirrorMaker 2 between Kafka and Redpanda
- Operational learning curve for the on-call rotation
- Cost: Redpanda Cloud licensing is approximately $480K annually vs current self-hosted Kafka at $290K annual TCO
