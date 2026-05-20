# Integration Guide: SAP EWM

This guide walks through integrating Acme's Fleet Manager with SAP Extended Warehouse Management (EWM). It's intended for customer IT teams and Acme deployment engineers working together on an SAP-based deployment.

## Prerequisites

Before starting the integration, the customer environment must meet:

- SAP EWM version 9.5 or higher (we support 9.5, 10.0, and Embedded EWM in S/4HANA)
- Network connectivity from Acme's WMS Connector service to the SAP system on TCP ports 4488 and 8000-8099
- A dedicated SAP service user with appropriate authorization profiles (see below)
- Active SAP RFC connection capability (SM59 transaction)

## Required SAP Authorization Profiles

The service user used by Acme's connector requires the following authorization objects:

- `/SCWM/MON` with activities 03 (display) and 06 (execute)
- `/SCWM/WHO` with activities 01 (create), 02 (change), 03 (display)
- `/SCWM/HU` with activities 01 (create), 02 (change), 03 (display), 06 (execute)
- `S_RFC` with function group `/SCWM/*`

If your security team requires more granular auth, contact your Acme deployment engineer — we have working configurations from past deployments we can share.

## Connection Setup

1. In SAP, create an RFC connection of type 3 (ABAP connection) pointing to Acme's connector endpoint provided by your deployment engineer.
2. Test the connection from SM59.
3. In Acme's Fleet Manager admin panel, add the customer SAP system under Settings → Integrations → SAP EWM.
4. Enter the SAP system parameters: hostname, client number, system ID, and the service user credentials.
5. Click "Test Connection" to verify bidirectional connectivity.

## Data Mapping

By default, Acme's connector maps the following SAP fields to internal Fleet Manager fields:

- SAP `WAREHOUSE_NO` → Fleet Manager `facility_id`
- SAP `HU_IDENT` (Handling Unit) → Fleet Manager `bin_id`
- SAP `WORK_ITEM_ID` → Fleet Manager `task_id`

For customers with non-standard SAP configurations, custom mappings can be defined in the connector's configuration YAML.

## Troubleshooting

**Connection times out during initial setup**

The most common cause is a firewall blocking the RFC ports. Verify with your network team that ports 4488 and 8000-8099 are open between the SAP system and the connector's IP range.

**Tasks appear in SAP but not in Fleet Manager**

This usually indicates a permission gap. Check that the service user has read access on `/SCWM/WHO`. The connector polls for new work orders every 30 seconds; if work orders exist but aren't appearing, run the diagnostic command in the admin panel to test polling.

**Stuck "in progress" tasks**

If tasks remain in "in progress" state in SAP after the robot has completed them, check the connector's outbound queue. Failed status updates are retried with exponential backoff up to 24 hours, then sent to a dead-letter queue for manual review.
