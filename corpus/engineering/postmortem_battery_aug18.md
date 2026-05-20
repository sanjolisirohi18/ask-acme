# Postmortem: WX-7 Battery Reporting Incident, August 18 2024

## Summary

On August 18, 2024, between 14:22 and 16:48 UTC, a software defect in firmware version 3.7.2 caused approximately 340 WX-7 robots across 9 customer facilities to report incorrect battery charge percentages to the Fleet Manager. The defect caused robots with 8-12% remaining charge to report 25-30%, resulting in 47 robots running out of power mid-task before being routed to charging stations.

No physical damage occurred. Customer operations at three facilities were paused for between 35 and 90 minutes while affected robots were manually retrieved and recharged.

## Root Cause

The defect was introduced in PR #4812, which refactored the battery state estimation code to use a Kalman filter for smoother readings. The refactor accidentally inverted the sign on the discharge correction term, causing the filter to over-estimate remaining capacity as the battery approached low-charge states.

The bug did not surface in our test suite because our unit tests used synthetic discharge curves that did not match the non-linear behavior of partially-aged batteries in the field.

## Timeline

- **August 12**: Firmware 3.7.2 begins gradual rollout (10% of fleet)
- **August 14**: Firmware 3.7.2 expanded to 50% of fleet, no anomalies reported
- **August 18 14:22**: First robot at Reno facility shuts down mid-pick
- **August 18 14:38**: Second and third robot shutdowns reported by Reno operator
- **August 18 14:45**: On-call engineer paged via PagerDuty
- **August 18 14:58**: Issue suspected to be firmware-related; rollback initiated via Argo CD
- **August 18 16:48**: All affected facilities back to normal operation

## Action Items

1. **Fix the sign error** in PR #4815 (completed, deployed Aug 19)
2. **Add field-data-driven battery tests** using anonymized telemetry from production fleet (assigned to firmware team, due Sep 15)
3. **Slow down firmware rollouts** for safety-critical changes — minimum 14 days at 10% before expansion (process change, effective immediately)
4. **Improve telemetry alerting** to flag anomalous discharge patterns before they cause shutdowns (assigned to platform team, due Oct 1)
