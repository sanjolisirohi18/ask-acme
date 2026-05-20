# Glossary of Acme-Specific Terms

This glossary defines internal terminology used across Acme Robotics engineering and product documentation.

## A

**ACS (Aisle Coordination System)** — the subsystem responsible for resolving conflicts when multiple robots need to traverse the same aisle simultaneously. Part of the dispatch-service.

**ARR-weighted churn** — customer churn weighted by annual recurring revenue rather than logo count. Used as our primary retention metric.

## B

**Bin pose** — the precise 6-degree-of-freedom position of a storage bin in a facility, used by the WX-7 manipulator to plan its pick approach.

**Brownout mode** — a degraded operational mode where robots reduce speed and disable non-essential subsystems to conserve battery. Triggered when battery drops below 15%.

## C

**Canary fleet** — the 10% of production robots used as the first wide-rollout stage for new firmware. Distributed across customer segments rather than concentrated at a single customer.

## D

**Dispatch decision** — a tuple of (task_id, robot_id, scheduled_time, route) emitted by the dispatch-service for each pick task. Stored in Postgres for audit.

## F

**Facility ID (fac-XXX)** — the unique identifier for a customer facility. Used as a partition key throughout the system. Format: `fac-{location_code}-{sequence}`, e.g., `fac-reno-01`.

**FleetOps** — internal nickname for the Fleet Manager operations team responsible for monitoring deployed fleets.

## G

**Ghost task** — a task that appears in dispatch-service but has no corresponding entry in the WMS. Almost always indicates a race condition during WMS sync. Should be auto-cancelled but historically caused dispatch loops.

## P

**Pick failure rate (PFR)** — the percentage of attempted picks that result in failure, regardless of cause. Tracked per robot per shift.

**PoseTrack** — the internal coordinate tracking system for robot localization. Built on top of LIDAR + visual odometry.

## R

**Rolling restart** — the deployment strategy for stateful services where pods are restarted one at a time to avoid service disruption.

## S

**Shadow mode** — an evaluation mode where new ML models run alongside the production model, with their outputs logged but not acted on. Used to validate model changes before promoting them.

**SLO budget** — the amount of error budget remaining in the current SLO window. When budget is exhausted, deploys are paused until the next window.

## T

**TPP (Tasks Per Pod)** — the throughput metric for the dispatch-service, measured as completed dispatch decisions per Kubernetes pod per minute.

**Twin** — an internal name for the digital twin of a physical robot, maintained in Fleet Manager. Each twin reflects the last known state of its corresponding physical robot.

## W

**WMS Connector** — the integration layer between Acme's Fleet Manager and customer warehouse management systems. Currently supports SAP EWM, Manhattan Active, Blue Yonder, Oracle WMS Cloud, and three smaller mid-market systems.
