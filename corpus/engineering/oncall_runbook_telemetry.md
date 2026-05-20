# On-Call Runbook: Telemetry Pipeline

This runbook covers the most common on-call scenarios for the telemetry-ingest service. It is owned by the Platform Infrastructure team.

## Alert: telemetry_lag_high

This alert fires when the consumer lag on the `robot-telemetry-raw` Kafka topic exceeds 30 seconds across any partition.

**Diagnostic steps:**

1. Check the Grafana dashboard at `fleet-ingest-overview`. Look at the per-partition lag chart.
2. If lag is isolated to one partition, the issue is likely a hot facility. Check which facility ID maps to the affected partition using the partition map in Confluence.
3. If lag is distributed across all partitions, the bottleneck is downstream. Check the `parquet-archiver` pod logs for write failures.

**Common causes:**

- S3 throttling during peak ingest windows (most common, especially during midnight UTC)
- A bad code deploy in the consumer (check recent CI/CD history)
- A new facility was added without scaling consumer replicas

**Mitigation:**

If the issue is S3 throttling, increase the parquet batch interval from 60 seconds to 120 seconds via the feature flag `archiver.batch_interval_seconds`. This trades latency for throughput.

If the issue is a bad deploy, roll back via Argo CD: `argocd app rollback fleet-telemetry --revision N-1`.

## Alert: command_control_disconnect_spike

This alert fires when more than 5% of connected robots in a facility disconnect from `command-control` within a 60-second window.

**Important:** Do not assume the robots are at fault. The most common cause is a network event at the customer site or a deploy of `command-control` itself.

Page the deployment engineer assigned to that facility (see PagerDuty rotation `field-deployments`). Do not attempt to remediate from the cloud side without coordinating with the on-site team.
