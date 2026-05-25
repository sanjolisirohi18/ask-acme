# Diagram 3a: Container Architecture (Static View)

The five runtime units that make up Ask Acme, with their external dependencies. Undirected lines indicate that two components communicate; direction of calls is shown in the dynamic diagrams (3b, 3c).

```mermaid
---
title: Ask Acme - Container Architecture (Static View)
---
flowchart TB
    User["Users <br/> Regular / Admin / Viewer"]
    Ingestion_Worker["Ingestion Worker <br/> Python process scheduled + on-demand ingest"]
    API_Service["API Service <br/> FastAPI process  <br/> queries, admin, auth, metrics"]
    Vector_DB["Vector Database <br/> Qdrant"]
    Relational_DB["Relational Database <br/> Postgres"]
    Cache_Rate_Limit["Cache / Rate-Limit Store <br/> Redis"]
    Local_FS["Local Filesystem <br/> markdown corpus"]
    Embedding_API["Embedding API <br/> OpenAI"]
    LLM_API["LLM API <br/> OpenAI / Anthropic"]

    subgraph AskAcme["Ask Acme System"]
        direction TB
        Ingestion_Worker
        API_Service
        Vector_DB
        Relational_DB
        Cache_Rate_Limit
    end

    subgraph External["External Dependencies"]
        direction TB
        Local_FS
        Embedding_API
        LLM_API
    end

    User --- API_Service

    API_Service --- Vector_DB
    API_Service --- Relational_DB
    API_Service --- Cache_Rate_Limit
    API_Service --- Embedding_API
    API_Service --- LLM_API

    Ingestion_Worker --- Vector_DB
    Ingestion_Worker --- Relational_DB
    Ingestion_Worker --- Embedding_API
    Ingestion_Worker --- Local_FS
```
