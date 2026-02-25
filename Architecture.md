# AI Restaurant Recommendation Service — Architecture

## Overview

This document describes the architecture for an **AI Restaurant Recommendation Service** that:
- Accepts user preferences: **price**, **place**, **rating**, **cuisine**
- Uses a **Groq LLM** to reason over restaurant data
- Returns **clear, ranked restaurant recommendations**

**Data source:** [Hugging Face — ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) (~51.7k rows, ~574 MB / ~152 MB Parquet)

**Frontend:** Next.js (Standard) / Streamlit (Deployment Ready)  
**LLM:** Groq

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NEXT.JS FRONTEND                                   │
│  (Preferences UI: price, place, rating, cuisine → Results display)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RECOMMENDATION API LAYER                             │
│  (REST/API routes: validate input, orchestrate retrieval + LLM)              │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                    │
                    ▼                                    ▼
┌──────────────────────────────┐    ┌──────────────────────────────────────────┐
│   RESTAURANT DATA LAYER      │    │            GROQ LLM LAYER                 │
│   (Hugging Face dataset       │    │   (Prompt + filtered candidates →         │
│    load, filter, cache)      │───▶│    reasoning & ranking → final list)       │
└──────────────────────────────┘    └──────────────────────────────────────────┘
```

---

## Phases

### Phase 1 — Data & Backend Foundation

**Goal:** Ingest Zomato data from Hugging Face and expose a minimal backend that can filter by price, place, rating, and cuisine.

| Component | Description |
|-----------|-------------|
| **Dataset integration** | Load `ManikaSaini/zomato-restaurant-recommendation` via Hugging Face `datasets` (or Parquet). Map columns to: price (or cost), place/location, rating, cuisine. Handle schema discovery and any column renaming/normalization. |
| **Data pipeline** | One-time or periodic load; optional export to local Parquet/JSON for faster reads. Define clear schema (TypeScript/JSON) for restaurant records used across the app. |
| **Filter service** | Backend module (e.g. Node/Next API or separate service) that filters restaurants by: price range, place/location, min rating, cuisine(s). Returns a **candidate set** (e.g. top N by relevance or rating). |
| **No LLM yet** | This phase only deals with data and filtering; no Groq calls. |

**Deliverables:**  
- Documented dataset schema (columns used for price, place, rating, cuisine).  
- Loader + filter API that returns filtered restaurant list for given preferences.

---

### Phase 2 — Groq LLM Integration

**Goal:** Use Groq LLM to turn the candidate set and user preferences into clear, natural-language recommendations.

| Component | Description |
|-----------|-------------|
| **Groq client** | Configure Groq API client (API key via env). Choose model (e.g. `llama-3.x` or Groq’s current default). |
| **Prompt design** | System + user prompts that include: (1) user preferences (price, place, rating, cuisine), (2) candidate restaurant list (structured: name, location, rating, price, cuisine, etc.). Ask the LLM to rank/select and explain in short, clear text. |
| **Recommendation service** | Orchestrator that: (1) gets candidates from Phase 1 filter service, (2) optionally truncates to top K (e.g. 20–50) to fit context, (3) calls Groq with prompt, (4) parses LLM output into a structured list (e.g. array of `{ name, reason }` or similar). |
| **Structured output** | Prefer structured output (JSON) from the LLM for reliable parsing; define a small response schema (e.g. list of recommended restaurants + short reason per item). |

**Deliverables:**  
- Groq integration module.  
- Prompt templates and response schema.  
- Recommendation API that returns LLM-ranked results with reasons.

---

### Phase 3 — Next.js Frontend

**Goal:** End-to-end UI: input preferences, call recommendation API, show results.

| Component | Description |
|-----------|-------------|
| **Preference form** | Next.js page(s) or components: inputs for **price** (range or tier), **place** (location/city), **rating** (min rating), **cuisine** (single/multi-select). Use client-side validation and clear labels. |
| **API consumption** | Call recommendation API (from Next API routes or server actions). Handle loading, errors, and empty results. |
| **Results UI** | Display ranked list: name, location, rating, price, cuisine, and LLM-generated reason. Optional: map link, images if present in dataset. |
| **State & UX** | Loading states, error messages, and optional “refine preferences” flow. |

**Deliverables:**  
- Next.js app with preference form and results view.  
- Responsive, accessible UI wired to the recommendation backend.

---

### Phase 4 — Reliability, Performance & Polish

**Goal:** Production-ready behavior: caching, rate limits, and observability.

| Component | Description |
|-----------|-------------|
| **Caching** | Cache filtered candidate sets or full recommendation responses (e.g. in-memory or Redis) keyed by normalized preferences to reduce Groq calls and latency. |
| **Rate limiting** | Rate limit recommendation API (per user or per IP) to respect Groq quotas and avoid abuse. |
| **Error handling** | Graceful handling of Groq failures, timeouts, and invalid responses; fallback to “filter-only” results or clear error message. |
| **Observability** | Log recommendation requests, latency, and failures; optional metrics (e.g. request count, cache hit rate). |
| **Security** | Keep Groq API key server-side only (Next.js API routes or backend service); never expose in frontend. |

**Deliverables:**  
- Caching and rate-limiting strategy and implementation.  
- Error-handling and fallback behavior.  
- Basic logging/metrics and security checklist.

---

## Technology Summary

| Layer | Technology |
|-------|------------|
| **Data** | Hugging Face `datasets` (or Parquet), ManikaSaini/zomato-restaurant-recommendation |
| **LLM** | Groq API (e.g. Llama 3 or Groq-hosted model) |
| **Backend / API** | Next.js API Routes (or separate Node service) |
| **Frontend** | Next.js (React) or Streamlit (Python) |
| **Optional** | Redis or in-memory cache; env-based config for API keys and feature flags |

---

## Data Flow (End-to-End)

1. **User** submits preferences (price, place, rating, cuisine) in the Next.js frontend.
2. **Frontend** sends request to Recommendation API (e.g. `POST /api/recommend`).
3. **API** calls **Data/Filter layer** → retrieves candidate restaurants from Zomato dataset (or cache).
4. **API** calls **Groq LLM** with preferences + candidate list; LLM returns ranked list with reasons.
5. **API** parses and returns structured recommendations to the frontend.
6. **Frontend** renders the list with names, details, and reasons.

---

## Out of Scope (Architecture Only)

- Implementation details (file structure, exact endpoints, and code).  
- Dataset schema is to be discovered in Phase 1; exact column names may be documented later in a separate schema file or in Phase 1 deliverables.

---

## Next Steps

1. **Phase 1:** add Hugging Face dataset loader, define internal restaurant schema, implement filter service and a minimal API.  
2. **Phase 2:** Add Groq client, design prompts and response format, implement recommendation service and recommendation API.  
3. **Phase 3:** Build Next.js UI (form + results) and connect to the API.  
4. **Phase 4:** Add caching, rate limiting, error handling, and observability.
