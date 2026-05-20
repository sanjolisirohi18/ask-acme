# 2025 Product Roadmap

This document outlines the product priorities for Acme Robotics in 2025. It is reviewed and updated quarterly by the product leadership team.

## Strategic Themes

For 2025, our three strategic themes are:

1. **Cold storage capability** — extending the WX-7 to operate in refrigerated and frozen warehouses (target operating range: -10°F to 35°F)
2. **Multi-robot coordination** — significantly improving how 50+ robots in a single facility share aisles and avoid deadlocks
3. **Customer self-service** — reducing the deployment time for new customers from 12 weeks to 4 weeks through better tooling

## Q1 2025

- **Cold storage prototype validation** in a customer pilot at Wendell Foods
- **Fleet Manager v3.0** release with redesigned operator UI and improved alerting
- **API v3 beta** with breaking changes for cleaner resource modeling

## Q2 2025

- **Cold storage GA** for select customers (first commercial deployment)
- **Multi-robot coordination v2** with priority-based path planning
- **Self-service deployment tools** alpha — internal use only initially

## Q3 2025

- **Cold storage expansion** to all customers
- **API v3 GA**, deprecation of API v2 begins (12-month sunset)
- **Self-service deployment** beta with three pilot customers

## Q4 2025

- **WX-8 hardware announcement** (next-generation robot, GA expected mid-2026)
- **Self-service deployment GA**
- **Localization** of operator UI to German, Polish, and Spanish

## Dependencies and Risks

The cold storage program depends on a hardware refresh of the WX-7's compute module. If supplier qualification slips, Q2 GA may move to Q3. The product team is monitoring this monthly with hardware engineering.

Multi-robot coordination depends on completing the path planner rewrite currently underway. The path planner team has consistently hit milestones on schedule, but the rewrite is technically ambitious and may surface surprises.
