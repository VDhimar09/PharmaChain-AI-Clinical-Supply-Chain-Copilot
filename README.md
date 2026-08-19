<div align="center">

# 💊 PharmaChain

### AI Clinical Supply Chain Copilot

**An explainable AI operations platform — deterministic reasoning plus RAG-grounded document Q&A — for pharmaceutical inventory,<br />warehouse capacity, shipment logistics and procurement decision support.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](backend/requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](backend/requirements.txt)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)](frontend/package.json)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](frontend/package.json)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](docker-compose.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](backend/Dockerfile)
[![License](https://img.shields.io/badge/License-MIT-3DA639?style=for-the-badge)](LICENSE.txt)

<img src="assets/screenshots/dashboard.jpg" width="100%" alt="PharmaChain Executive Dashboard" />

<sub>Executive Dashboard — live operational KPIs served from the FastAPI backend</sub>

</div>

> [!NOTE]
> PharmaChain combines a **deterministic, rule-based Executive Copilot** for live operational reasoning with a **RAG pipeline** (pgvector retrieval + OpenAI-backed grounded generation) for document Q&A, integrated at an explicit evidence boundary (`GroundedCopilotService`) that keeps operational and document evidence separated and auditable. `OPENAI_API_KEY` is required and actively used for RAG embeddings and grounded generation; `AZURE_OPENAI_*` remain **reserved, currently-unused** settings for a future Azure OpenAI provider. Every claim in this README is verified against the actual codebase.

---

## 📚 Table of Contents

<table>
<tr>
<td valign="top" width="50%">

- [📖 Overview](#-overview)
- [✨ Features](#-features)
- [🏗️ Architecture](#-architecture)
- [🛠️ Technology Stack](#-technology-stack)
- [📂 Folder Structure](#-folder-structure)
- [🔌 API Reference](#-api-reference)

</td>
<td valign="top" width="50%">

- [🔐 Authentication & RBAC](#-authentication--rbac)
- [🚀 Getting Started](#-getting-started)
- [🧪 Testing](#-testing)
- [☁️ Deployment](#-deployment)
- [🗺️ Roadmap](#-roadmap)
- [🖼️ Screenshots](#-screenshots-gallery) · [👩‍💻 About](#-about) · [📄 License](#-license)

</td>
</tr>
</table>

---

## 📖 Overview

Pharmaceutical supply chains carry risk that generic dashboards miss: cold-chain inventory with strict expiry windows, warehouse zones with finite shared capacity, shipment delays that ripple silently into stockouts, and procurement calls made without a consolidated, auditable view of stock, incoming shipments and supplier reliability. **PharmaChain** consolidates inventory, warehouse, shipments and procurement behind one authenticated, role-aware application, and adds an AI layer that reasons over **live** operational data — every KPI, table and chart reads from PostgreSQL through the FastAPI service layer, nothing is hardcoded or simulated.

It's built for operations, warehouse and procurement managers who need one place to see inventory health, warehouse occupancy, shipment risk and an explainable procurement recommendation — and for engineers evaluating a realistic, full-stack, RBAC-secured FastAPI + React reference implementation.

A procurement or capacity decision made without evidence is hard to trust and hard to audit later. PharmaChain's reasoning engine makes every AI answer traceable: detected intent → execution plan → tools run → evidence collected → composed recommendation with a confidence score, all inspectable in the UI rather than hidden behind a black box.

---

## ✨ Features

- **📊 Dashboard** — Executive KPIs (inventory units, warehouse occupancy, incoming/delayed shipments) from `GET /api/dashboard/summary`, plus AI-generated priorities from `GET /api/ai/insights`.
- **📦 Inventory** — Live inventory table and status KPIs (Healthy / Low / Critical / Expiring) from `GET /api/inventory`, with status computed server-side from quantity and expiry date.
- **🏭 Warehouse** — Zone-level capacity and occupancy from `GET /api/warehouse-zones` and `/capacity`. Forecasting isn't implemented server-side, so forecast widgets honestly show **Unavailable** instead of fabricated numbers.
- **🚚 Shipments** — Shipment table and status KPIs (In Transit / Delivered / Delayed / Processing) from `GET /api/shipments`.
- **🤖 AI Procurement** — Compose a request (product, supplier, quantity) and run it through the reasoning engine via `POST /api/ai/procurement/analyze` — returns a decision, confidence score, tool execution trace, reasoning steps and evidence bundle.
- **📈 AI Insights** — A single operations centre — executive KPIs, alerts, inventory/warehouse/shipment/procurement breakdowns, recommendations and trend charts — all from one call to `GET /api/ai/insights`.
- **💬 Executive Copilot** — A conversational interface over the same reasoning engine (`POST /api/ai/copilot/chat`) — ask an operational question, get a structured, explainable answer with its tool execution trace. Questions that also need documented policy (e.g. *"Why is shipment SH-102 at risk, and what does our cold-chain SOP require?"*) are additionally grounded in retrieved document evidence — see [Grounded Copilot](#-grounded-copilot-rag--executive-copilot).
- **📚 Document Q&A (RAG)** — Upload PDFs (SOPs, policies, procedures), then ask questions answered strictly from retrieved chunks via `POST /api/rag/query` — citations are validated server-side and fabricated sources are never surfaced (`POST /api/documents`, `POST /api/rag/search`, `POST /api/rag/query`).
- **🔐 Auth & RBAC** — JWT access/refresh tokens and five permission-scoped roles gate every route in the API — see [Authentication & RBAC](#-authentication--rbac).

> All seven modules are pictured together in the [Screenshots Gallery](#-screenshots-gallery).

---

## 🏗️ Architecture

### System Architecture

<div align="center">

```mermaid
graph TD
    A["⚛️ React Frontend<br/>TanStack Router + Query"] -- "HTTPS / JSON<br/>Bearer JWT" --> B

    subgraph Backend["FastAPI Backend"]
        B["🔌 API Layer<br/>app/api/*.py"] --> C["🔐 Auth & RBAC<br/>get_current_user / require_permission"]
        C --> D["🧠 Service Layer<br/>app/services/*.py"]
        D --> E["📚 Repository Layer<br/>app/repositories/*.py"]
        D --> F["🤖 AI Reasoning Engine<br/>app/ai/*"]
        G["⏱️ APScheduler<br/>background jobs"] --> E
    end

    E --> H[("🐘 PostgreSQL 16")]
    F --> E

    style H fill:#336791,color:#fff
    style F fill:#6d4aff,color:#fff
```

</div>

Real backend layering: `api/` (FastAPI routers) → `services/` (business logic) → `repositories/` (data access) → SQLAlchemy models → PostgreSQL. A background APScheduler job (`app/jobs/shipment_monitor.py`) writes to the same repository layer on a schedule.

### AI Reasoning Pipeline

<div align="center">

```mermaid
graph TD
    U(("🧑 User")) --> R["⚛️ React<br/>AI Procurement / Executive Copilot page"]
    R -- "POST /api/ai/copilot/chat<br/>POST /api/ai/procurement/analyze" --> API["🔌 FastAPI"]
    API --> INT["🎯 Intent Engine"]
    INT --> PLAN["🗺️ ReasoningPlanner → RuleBasedPlanner<br/>builds ExecutionPlan"]
    PLAN --> ENGINE["⚙️ ReasoningEngine"]
    ENGINE --> REG["🧰 ToolRegistry"]
    REG --> T1["Inventory Tool"]
    REG --> T2["Warehouse Tool"]
    REG --> T3["Shipment Tool"]
    REG --> T4["Procurement Tool"]
    T1 & T2 & T3 & T4 --> REPO["📚 Repositories"]
    REPO --> DB[("🐘 PostgreSQL")]
    ENGINE --> COMP["✍️ ResponseComposer<br/>evidence → explainable answer"]
    COMP --> API
    API --> R
    R --> U

    OAI["🔮 OpenAI / Azure OpenAI<br/><i>reserved for a future<br/>LLM-backed planner</i>"]
    PLAN -.->|"not called today"| OAI

    style OAI fill:#f5f5f5,color:#999,stroke-dasharray:5 5
    style DB fill:#336791,color:#fff
```

</div>

This mirrors the pipeline documented in [`backend/docs/architecture.md`](backend/docs/architecture.md): `CopilotTool → ReasoningPlanner → PlanningStrategy → RuleBasedPlanner → ExecutionPlan → ReasoningEngine → ToolRegistry → Tools → ResponseComposer`. The planner is built with the Strategy pattern specifically so an `LLMPlanner` can be substituted later without touching the execution or response layers — but no such planner exists in the codebase today.

Three UI surfaces drive this pipeline directly:

| Page | Endpoint | Service |
|---|---|---|
| `/assistant` — AI Procurement | `POST /api/ai/procurement/analyze` | `ProcurementAnalysisService` |
| `/insights` — AI Insights | `GET /api/ai/insights` | `AIInsightsService` |
| `/copilot` — Executive Copilot | `POST /api/ai/copilot/chat` | `GroundedCopilotService` (routes to `CopilotOrchestratorService` for operational-only questions) |

`/assistant` and `/insights` never call an external LLM — both run the same in-process `ReasoningPlanner → RuleBasedPlanner → ReasoningEngine → ToolRegistry` pipeline. `/copilot` runs that identical deterministic pipeline too for operational-only questions, but a question that also needs document evidence additionally invokes RAG's grounded LLM synthesis — see [Grounded Copilot](#-grounded-copilot-rag--executive-copilot). In every case, intent, tool execution trace, evidence and reasoning are returned directly to the UI, so every answer is auditable rather than just readable.

### 🔗 Grounded Copilot (RAG + Executive Copilot)

The Executive Copilot above and the RAG document pipeline ([Document Q&A](#-features)) were built as two independent systems and are integrated at a single, explicit boundary: **`GroundedCopilotService`** (`POST /api/ai/copilot/chat`). It does not replace either system or turn RAG into "just another tool" — operational evidence (live DB facts) and document evidence (retrieved PDF chunks) are kept strictly separated end-to-end:

1. `EvidenceRequirementDetector` classifies the question as `OPERATIONAL`, `DOCUMENT`, or `OPERATIONAL_AND_DOCUMENT` (deterministic keyword/intent check, not an LLM call).
2. **Operational-only** → the existing `CopilotOrchestratorService` pipeline runs unchanged; still no LLM call, identical behavior to before Phase 3.
3. **Document-only** → the existing `RagGenerationService` runs unchanged (retrieval → bounded context → LLM → server-side citation validation → fixed no-evidence fallback if nothing was retrieved).
4. **Both** → operational evidence (`CopilotEvidenceBundle`) and document evidence (`RetrieverService` + `ContextBuilder`) are gathered independently, then combined into one LLM synthesis call that is instructed to keep the two kinds of evidence distinct and to cite document evidence only. Citations are re-validated server-side against the retrieved chunks — a `SOURCE_N` id the model invents is dropped, and an answer that cites nothing real is discarded in favor of the trustworthy deterministic operational answer.
5. **RBAC**: document evidence is only ever fetched if the caller also holds `rag.query` — `copilot.use` alone never grants it. A combined question from a caller without `rag.query` still gets an operational answer; a document-only question from that caller is rejected with 403.

The response schema (`CopilotChatResponse`) is backward compatible — `evidence_requirement`, `grounded`, `document_evidence` and `citations` are additive, defaulted fields, so every pre-Phase-3 caller keeps working unchanged. The `/copilot` page renders all four directly per answer: an evidence-requirement badge (Operational / Document / Operational + Document), a grounded / no-document-evidence badge, an operational-evidence checklist (tool execution), and a document-sources list of server-validated citations only — never raw, unvalidated chunks. Document-oriented suggested prompts are only offered to users holding `rag.query`. See [`backend/docs/architecture.md`](backend/docs/architecture.md) for the full write-up.

---

## 🛠️ Technology Stack

<table>
<tr><th>Layer</th><th>Technology</th></tr>
<tr>
<td><b>Frontend</b></td>
<td>React 19 · TypeScript 5 · TanStack Router / Start · TanStack Query · Tailwind CSS 4 · Radix UI · Recharts · React Hook Form · Zod · Vite 7</td>
</tr>
<tr>
<td><b>Backend</b></td>
<td>FastAPI · Python 3.13 · SQLAlchemy 2.0 · Alembic · Pydantic 2 · APScheduler</td>
</tr>
<tr>
<td><b>Database</b></td>
<td>PostgreSQL 16 · psycopg2-binary</td>
</tr>
<tr>
<td><b>AI</b></td>
<td><b>Operational reasoning</b> — deterministic, rule-based (Intent Engine → Planner → Tool Registry → Response Composer), no LLM call. <b>RAG / Grounded Copilot</b> — OpenAI (<code>text-embedding-3-small</code> embeddings, <code>gpt-4o-mini</code> generation) via <code>OPENAI_API_KEY</code>, actively used for document retrieval and grounded synthesis. <code>AZURE_OPENAI_*</code> remain reserved, unused.</td>
</tr>
<tr>
<td><b>Authentication</b></td>
<td>JWT (PyJWT, HS256) access + refresh tokens · passlib + bcrypt password hashing · permission-based RBAC</td>
</tr>
<tr>
<td><b>Deployment</b></td>
<td>Docker (backend), Dockerfile configured for Render; frontend built via Vite/Nitro</td>
</tr>
</table>

---

## 📂 Folder Structure

<details>
<summary><b>Click to expand full repository layout</b></summary>

```text
PharmaChain-AI-Clinical-Supply-Chain-Copilot/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── planner/        # PlannerContext, PlanningStrategy, RuleBasedPlanner, ReasoningPlanner
│   │   │   ├── reasoning/      # ReasoningEngine
│   │   │   ├── response/       # ResponseComposer
│   │   │   └── tools/          # ToolRegistry + Inventory/Warehouse/Shipment/Procurement tools
│   │   ├── api/                 # FastAPI routers (one file per domain)
│   │   ├── core/                 # config, database, security (JWT), logging
│   │   ├── dependencies/        # get_current_user, require_permission, require_role
│   │   ├── jobs/                 # APScheduler background jobs (shipment monitor)
│   │   ├── models/               # SQLAlchemy models
│   │   ├── repositories/        # Data-access layer
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Business logic / orchestration
│   │   └── main.py               # App factory, router registration, startup/shutdown
│   ├── alembic/                  # Database migrations
│   ├── tests/                    # pytest suite (33 test modules)
│   ├── docs/architecture.md      # AI reasoning pipeline documentation
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── routes/                # TanStack Router file-based routes (one per page)
│       ├── components/
│       │   ├── copilot/           # Executive Copilot UI
│       │   ├── insights/          # AI Insights UI
│       │   ├── procurement/       # AI Procurement UI
│       │   └── ui/                # Shared Radix/shadcn-style primitives
│       ├── hooks/
│       └── lib/
│           ├── api/               # apiClient, endpoints.ts, React Query hooks.ts
│           └── auth/              # Token storage
├── assets/
│   └── screenshots/               # Product screenshots used in this README
├── docker-compose.yml
└── README.md
```

</details>

---

## 🔌 API Reference

All routes require a valid JWT unless marked **Public**; most also require the listed permission via `require_permission(...)`.

<details open>
<summary><b>Inventory · Warehouse · Shipments</b></summary>

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| `GET` | `/api/inventory/` | List all inventory records | `inventory.read` |
| `GET` | `/api/inventory/statistics` | Aggregate inventory statistics | `inventory.read` |
| `GET` | `/api/inventory/low-stock` | Items at/under safety stock | `inventory.read` |
| `GET` | `/api/inventory/expiring` | Items expiring within 30 days | `inventory.read` |
| `GET` | `/api/inventory/{id}` | Get one inventory record | `inventory.read` |
| `POST` | `/api/inventory/` | Create an inventory record | `inventory.write` |
| `DELETE` | `/api/inventory/{id}` | Delete an inventory record | `inventory.write` |
| `GET` | `/api/warehouse-zones/` | List warehouse zones | `warehouse.read` |
| `GET` | `/api/warehouse-zones/capacity` | Aggregate capacity summary | `warehouse.read` |
| `GET` | `/api/warehouse-zones/{id}` | Get one zone | `warehouse.read` |
| `POST` | `/api/warehouse-zones/` | Create a zone | `warehouse.write` |
| `DELETE` | `/api/warehouse-zones/{id}` | Delete a zone | `warehouse.write` |
| `GET` | `/api/shipments/` | List shipments | `shipment.read` |
| `GET` | `/api/shipments/statistics` | Shipment statistics | `shipment.read` |
| `GET` | `/api/shipments/{id}` | Get one shipment | `shipment.read` |
| `POST` | `/api/shipments/` | Create a shipment | `shipment.write` |
| `DELETE` | `/api/shipments/{id}` | Delete a shipment | `shipment.write` |

</details>

<details>
<summary><b>Products · Suppliers · Procurement</b></summary>

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| `GET` | `/api/products/` | List products | `inventory.read` |
| `POST` | `/api/products/` | Create a product | `inventory.write` |
| `GET` | `/api/suppliers/` | List suppliers | `supplier.read` |
| `POST` | `/api/suppliers/` | Create a supplier | `supplier.write` |
| `GET` | `/api/procurement-requests/` | List procurement requests | `procurement.read` |
| `GET` | `/api/procurement-requests/statistics` | Procurement statistics | `procurement.read` |
| `GET` | `/api/procurement-requests/{id}` | Get one request | `procurement.read` |
| `POST` | `/api/procurement-requests/` | Create a procurement request | `procurement.write` |
| `DELETE` | `/api/procurement-requests/{id}` | Delete a procurement request | `procurement.write` |
| `POST` | `/api/procurement-ai/evaluate` | Rule-based procurement evaluation | `ai.access` |

</details>

<details>
<summary><b>AI, Dashboard, Audit & System</b></summary>

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| `GET` | `/api/ai/insights` | Full AI Insights payload | `insights.view` |
| `POST` | `/api/ai/copilot/chat` | Executive Copilot — operational and/or document-grounded, see [Grounded Copilot](#-grounded-copilot-rag--executive-copilot) | `copilot.use` (+ `rag.query` for document evidence) |
| `POST` | `/api/documents/upload` | Upload a PDF for RAG ingestion | `documents.upload` |
| `GET` | `/api/documents/` | List uploaded documents | `documents.read` |
| `DELETE` | `/api/documents/{id}` | Delete an uploaded document | `documents.delete` |
| `POST` | `/api/rag/search` | Semantic search over ingested chunks (evidence only, no LLM) | `rag.search` |
| `POST` | `/api/rag/query` | Grounded, citation-validated Q&A over ingested documents | `rag.query` |
| `POST` | `/api/ai/procurement/analyze` | Deterministic AI procurement analysis with reasoning trace | `ai.access` |
| `GET` | `/api/ai/inventory-summary` | Inventory tool summary (internal/legacy) | `insights.view` |
| `GET` | `/api/ai/low-stock` | Low-stock tool output (internal/legacy) | `insights.view` |
| `GET` | `/api/ai/expiring` | Expiring-products tool output (internal/legacy) | `insights.view` |
| `GET` | `/api/ai/warehouse-capacity` | Warehouse tool capacity summary (internal/legacy) | `insights.view` |
| `GET` | `/api/ai/shipment-summary` | Shipment tool summary (internal/legacy) | `insights.view` |
| `POST` | `/api/chat/` | Alternate chat endpoint (`AIChatService`) | `copilot.use` |
| `GET` | `/api/dashboard/summary` | Executive KPI summary | `insights.view` |
| `GET` | `/api/audit/` | Paginated, filterable audit log query | `audit.read` |
| `GET` | `/api/system/jobs/` | Background scheduler job health | `system.monitor` |
| `GET` | `/` | API welcome message | Public |
| `GET` | `/health` | Health check | Public |
| `GET` | `/docs` | Interactive OpenAPI (Swagger) docs | Public |

</details>

<details>
<summary><b>Authentication</b></summary>

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/auth/login` | Authenticate, returns access + refresh tokens | Public |
| `POST` | `/api/auth/refresh` | Exchange refresh token for a new token pair | Public |
| `POST` | `/api/auth/logout` | Revoke a refresh token | Authenticated |
| `GET` | `/api/auth/me` | Current user's profile, role and permissions | Authenticated |

</details>

---

## 🔐 Authentication & RBAC

| Aspect | Detail |
|---|---|
| **JWT** | Login issues a short-lived **access token** and a longer-lived **refresh token**, signed with `PyJWT` (`HS256`). |
| **Refresh tokens** | Persisted server-side (`RefreshToken` model) and individually revocable on logout; default lifetimes are **15 minutes** (access) and **7 days** (refresh), both configurable. |
| **RBAC** | Permission-based — every protected route depends on `require_permission("<permission>")`, and a role is a named bundle of permission strings. `system.admin` is a superuser permission that satisfies every check. |
| **Protected routes** | Every domain router (`inventory`, `warehouse-zones`, `shipments`, `products`, `suppliers`, `procurement-requests`, `ai`, `dashboard`, `audit`, `system/jobs`, `documents`, `rag`) is mounted behind `get_current_user`, and each endpoint additionally checks a specific permission. |
| **Copilot + RAG boundary** | `copilot.use` never implicitly grants `rag.query`. `GroundedCopilotService` checks both independently — a caller with only `copilot.use` still gets operational Copilot answers, but document evidence is never fetched on their behalf. |

<details>
<summary><b>Built-in roles and their permissions</b></summary>

| Role | Permissions |
|---|---|
| **Administrator** | `system.admin` (all), plus every domain read/write/approve permission, including `documents.*` and `rag.search`/`rag.query` |
| **Operations Manager** | `inventory.read`, `warehouse.read`, `shipment.read`, `procurement.read`, `insights.view`, `copilot.use`, `documents.read`, `rag.search`, `rag.query` |
| **Warehouse Manager** | `inventory.read`, `inventory.write`, `warehouse.read`, `warehouse.write`, `shipment.read`, `copilot.use` — **no** `rag.*`/`documents.*` (Copilot stays operational-only for this role, even for combined questions) |
| **Procurement Manager** | `supplier.read`, `supplier.write`, `procurement.read`, `procurement.write`, `procurement.approve`, `inventory.read`, `insights.view`, `copilot.use` — **no** `rag.*`/`documents.*` |
| **Viewer** | `inventory.read`, `warehouse.read`, `shipment.read`, `supplier.read`, `procurement.read`, `insights.view`, `documents.read`, `rag.search`, `rag.query` (no `copilot.use`) |

Roles and permissions are seeded automatically on startup by `BootstrapService`, along with a default administrator controlled by the `BOOTSTRAP_ADMIN_*` environment variables.

</details>

---

## 🚀 Getting Started

### Clone

```bash
git clone https://github.com/VDhimar09/PharmaChain-AI-Clinical-Supply-Chain-Copilot.git
cd PharmaChain-AI-Clinical-Supply-Chain-Copilot
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

On startup, the backend automatically creates tables, seeds RBAC roles/permissions, creates a bootstrap administrator, and seeds demo data — no manual database setup required beyond a running PostgreSQL instance.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

<details>
<summary><b><code>backend/.env</code></b></summary>

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — (required) | PostgreSQL connection string |
| `JWT_SECRET_KEY` | `change-me-in-production` | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `JWT_ISSUER` | `pharmachain-api` | JWT issuer claim |
| `BOOTSTRAP_ADMIN_EMAIL` | `admin@pharmachain.com` | Seeded administrator email |
| `BOOTSTRAP_ADMIN_PASSWORD` | `ChangeMe123!` | Seeded administrator password — change before any shared deployment |
| `BOOTSTRAP_ADMIN_NAME` | `PharmaChain Administrator` | Seeded administrator display name |
| `OPENAI_API_KEY` | *(empty)* | Required for OpenAI embeddings and grounded generation (`gpt-4o-mini`). Local embeddings do not require it, but grounded generation still does. |
| `RAG_EMBEDDING_PROVIDER` | `openai` | Embedding profile: `openai` uses 1536-dimensional OpenAI vectors; `local` uses the CPU-local `sentence-transformers/all-MiniLM-L6-v2` 384-dimensional profile. Profiles are stored and retrieved separately. |
| `RAG_LOCAL_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local model downloaded once by Sentence Transformers to the developer's Hugging Face cache, outside the repository. |
| `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_API_KEY` | *(empty)* | Reserved for a future Azure OpenAI provider — not currently used |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Comma-separated allowed origins |
| `ENVIRONMENT` | `development` | Environment label |

</details>

<details>
<summary><b><code>frontend/.env</code></b></summary>

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Base URL the frontend calls for all `/api/*` requests |

</details>

### Running Locally

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

### Docker

```bash
docker compose up --build
```

Starts PostgreSQL 16 and the FastAPI backend (`backend/Dockerfile`). Run the frontend separately with `npm run dev` / `npm run build`.

---

## 🧪 Testing

**Backend** — pytest suite in `backend/tests/` (33 test modules), covering authentication, RBAC, audit logging, the AI planner/reasoning engine/tool registry/response composer, procurement AI/analysis services, background job integration, the RAG pipeline (parsing, chunking, embeddings, retrieval, grounded generation) and the grounded Copilot integration (evidence contract, evidence-requirement detection, citation resolution, RBAC boundary). Currently **286 passed, 0 failed**.

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

**Frontend** — no automated test suite is currently configured (`frontend/package.json` has no `test` script). Verification today is `npm exec tsc --noEmit` + `eslint` + `npm run build`.

---

## ☁️ Deployment

- **Backend** — `backend/Dockerfile` is written for containerized deployment and is explicitly configured for **Render** (reads `$PORT`, installs from `requirements.txt`).
- **Frontend** — built with Vite + TanStack Start on the Nitro server target; `npm run build` produces a deployable server bundle. This repository's default Nitro preset emits a Cloudflare Workers–compatible output.
- No **Vercel** configuration and no CI/CD pipeline (e.g. GitHub Actions) currently exist in this repository — they are not claimed here.

---

## 🗺️ Roadmap

**Completed**

- [x] Full CRUD-backed Inventory, Warehouse Zones, Shipments, Products, Suppliers and Procurement Requests modules
- [x] JWT auth with refresh tokens and five-role, permission-based RBAC
- [x] Deterministic AI reasoning engine — Intent Engine → Planner → Tool Registry → Response Composer
- [x] AI Procurement analysis, AI Insights operations centre and Executive Copilot chat
- [x] Audit logging and background shipment-monitor job (APScheduler)
- [x] Core frontend pages (Dashboard, Inventory, Warehouse, Shipments) migrated from mock data onto live backend endpoints
- [x] Retrieval-Augmented Generation (RAG) over uploaded PDF documents — ingestion, pgvector similarity search, grounded LLM generation with server-side citation validation (`POST /api/rag/query`)
- [x] Grounded Executive Copilot — RAG integrated into the Copilot at an explicit evidence boundary (`GroundedCopilotService`) so operational and document evidence stay separated end-to-end — see [Grounded Copilot](#-grounded-copilot-rag--executive-copilot)
- [x] Grounded Copilot frontend UI — evidence-requirement and grounded-status badges, an operational-evidence checklist, and validated document-source citations rendered per answer on the `/copilot` page, with document-oriented prompts gated behind `rag.query`

**Future**

- [ ] LLM-backed planning strategy for the deterministic operational Copilot (`OPENAI_API_KEY` is already configured and in active use for RAG; a future `LLMPlanner` could reuse it — `AZURE_OPENAI_*` remain unused)
- [ ] Redis caching layer
- [ ] CI/CD pipeline (e.g. GitHub Actions)
- [ ] Automated frontend test suite
- [ ] Kubernetes deployment manifests
- [ ] Monitoring & observability beyond the current audit log

---

## 🖼️ Screenshots Gallery

<p align="center">
  <img src="assets/screenshots/dashboard.jpg" width="49%" alt="Dashboard" />
  <img src="assets/screenshots/inventory.jpg" width="49%" alt="Inventory" />
</p>
<p align="center">
  <img src="assets/screenshots/warehouse-capacity.jpg" width="49%" alt="Warehouse Capacity" />
  <img src="assets/screenshots/shipments.jpg" width="49%" alt="Shipments" />
</p>
<p align="center">
  <img src="assets/screenshots/ai-procurement.jpg" width="49%" alt="AI Procurement" />
  <img src="assets/screenshots/ai-insights.jpg" width="49%" alt="AI Insights" />
</p>
<p align="center">
  <img src="assets/screenshots/executive-copilot.jpg" width="49%" alt="Executive Copilot" />
</p>

---

## 👩‍💻 About

<div align="center">

**Vibhuti Dhimar**

AI Software Engineer · Product Engineer · NHS Tech Returner

This project demonstrates full-stack engineering and explainable AI system design — deterministic operational reasoning combined with RAG-grounded document retrieval — through a realistic pharmaceutical supply chain platform.

[![GitHub](https://img.shields.io/badge/GitHub-VDhimar09-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VDhimar09)

</div>

---

## 📄 License

<div align="center">

Licensed under the **MIT License** — see [`LICENSE.txt`](LICENSE.txt).

<sub>Built with FastAPI, React, PostgreSQL, a deterministic reasoning engine and a RAG/grounded LLM pipeline.</sub>

</div>
