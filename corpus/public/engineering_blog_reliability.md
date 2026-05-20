# Engineering Blog: How We Build Reliable Robots

*Posted September 30, 2024 by Priya Vasquez, CTO*

When we started Acme Robotics seven years ago, I had a thesis: reliability in warehouse robotics is not primarily a hardware problem, it's a software problem. Seven years and 4,800 robots later, I'm more convinced than ever.

This post is a candid look at how we've built reliability into our engineering culture. It's written for fellow engineers — there's no marketing in here.

## The Problem with "Move Fast and Break Things" for Robots

In typical SaaS, breaking things in production is annoying but recoverable. Roll back, ship a hotfix, write a post-mortem, move on. In robotics, breaking things in production means a 200-pound robot in a customer warehouse behaving unpredictably. The blast radius is physical, immediate, and visible to humans walking nearby.

So we've built our culture around two principles: aggressive testing in simulation, and conservative rollouts in the field.

## Simulation First

Every motion-planning change is tested against a simulation harness with over 10,000 recorded scenarios from real customer deployments. The simulation runs in CI for every PR that touches motion code. A change cannot merge if it causes a regression in any scenario.

We treat the simulation harness as a first-class engineering investment. Three engineers work on it full-time. Their job is to make sure simulation tracks reality as closely as possible.

## Graduated Rollouts

When we ship a firmware update, it goes through five rollout stages:

1. **Internal test fleet** (week 1): 8 robots in our Austin office
2. **Friendly customer pilot** (week 2-3): 30 robots at 2 customers who have opted into early access
3. **10% canary** (week 4-5): roughly 480 robots, distributed across customer segments
4. **50% rollout** (week 6-7): half the fleet
5. **Full rollout** (week 8+): remaining robots

At any stage, our anomaly detection can halt the rollout if telemetry deviates from baseline. This has saved us from several near-misses, including a battery management bug that surfaced at the 10% canary stage in August 2024 before causing customer impact.

## What We Got Wrong

We didn't always do this well. In 2021, a firmware bug caused 17 robots to enter a tight turning loop in a customer's facility. No physical damage, but the customer was understandably alarmed. That incident is why we built the simulation harness — we'd been relying on "the code looks right" and on small-scale testing, both of which are insufficient at the scales we operate at now.

## What's Next

We're investing heavily in chaos engineering for the cloud-to-robot control plane. The idea: deliberately inject failures (network partitions, slow disks, message reordering) into our staging environment and ensure the fleet remains safe. If you find that interesting, we're hiring.
