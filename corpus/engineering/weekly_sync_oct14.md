# Platform Infra Weekly Sync — October 14, 2024

Attendees: Diana Schmidt, Marcus Yoon, Felix Tran, Priya Vasquez (manager), Aisha Patel (visiting from path-planner team)

## Status Updates

### Diana
- Finished the migration of fleet-ui to Next.js 14. No regressions reported.
- Started looking into the Redpanda migration — initial benchmarks look promising
- Blocked on: needs review on PR #5102 (Diana → Felix)

### Marcus
- On-call last week. Two pages, both were the S3 throttling issue. Filed the action item from last quarter's retro that we still haven't done.
- Wrapping up the OpenTelemetry rollout. About 80% of services emitting traces now.
- Question for Priya: do we want OTel metrics in addition to Prometheus, or stick with Prom for metrics?

### Felix
- Pairing with Aisha on a perf issue in the path-planner — it's spending 40% of CPU in serialization. We think we can cut that in half with a different protobuf layout.
- Will write up findings as a doc once we have numbers.

## Decisions

1. **Redpanda migration** — proceed to Phase 1 (us-east-1 standup). Diana to write design doc, target review by end of October. Priya to bring to architecture review.

2. **OTel for metrics** — defer the decision. Prometheus is working fine for metrics; OTel rollout focuses on traces and logs for now.

3. **Path-planner perf work** — Felix and Aisha continue pairing through end of month. If gains hold up, propose protobuf change for v3.0 path planner.

## Action Items

- [ ] Diana: Redpanda design doc draft by Oct 28
- [ ] Marcus: Schedule retro action item review (we have 3 unaddressed items from August)
- [ ] Felix: Document path-planner profiling findings by Oct 21
- [ ] Priya: Sync with hardware team on the Krakow office expansion timeline

## Random Thoughts / Parking Lot

- Aisha mentioned the path-planner team is interested in feature flags. Felix volunteered to do a 30-min walkthrough of LaunchDarkly.
- We should think about whether the alerting service should move off Python. It's the only Python service in the critical path and the cold-start time is annoying. Not urgent.
