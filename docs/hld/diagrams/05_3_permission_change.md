# Diagram 5.3: Permission Change Mid-Session (UC-5)

Demonstrates NFR-13: permission decisions are not cached across requests. A permission grant by an admin takes effect on the user's next query without re-authentication.

```mermaid
---
title: Ask Acme - Permission Change Mid-Session (UC-5)
---
sequenceDiagram
    actor user as Felix(Regular User)
    actor admin as Diana(Admin)
    participant api_service as API Service
    participant postgres as Postgres

    Note over user: groups{public,eng-shared,eng-platform}
    user ->>+ api_service: POST /ask {path-planner question}
    api_service ->>+ postgres: resolve user + content groups
    postgres -->>- api_service: groups{public,eng-shared,eng-platform}
    Note over api_service: retrieval + generation <br/> (no eng-path-planner chunks visible)
    api_service -->>- user: "No relevant information found."
    admin ->>+ api_service: POST /admin/users/felix/groups {add:eng-path-planner}
    api_service ->>+ postgres: insert USER_GROUPS row (felix, eng-path-planner, granted_by=diana)
    postgres -->>- api_service: ok
    api_service -->>- admin: 200 OK
    Note over user: same bearer token, <br/> no re-authentication
    user ->>+ api_service: POST /ask {path-planner question}
    api_service ->>+ postgres: resolve user + content groups
    postgres -->>- api_service: groups{public,eng-shared,eng-platform,eng-path-planner}
    Note over api_service: retrieval + generation <br/> (eng-path-planner chunks now visible)
    api_service -->>- user: {answer with eng-path-planner citations}
```
