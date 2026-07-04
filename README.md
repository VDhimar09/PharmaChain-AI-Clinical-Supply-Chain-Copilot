# 💊 PharmaChain – AI Clinical Supply Chain Copilot

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-12%20Passing-brightgreen)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

PharmaChain is an enterprise AI-powered Clinical Supply Chain Copilot built for pharmaceutical warehouses and clinical supply chain teams. It combines modern AI reasoning with a production-oriented backend architecture to support inventory visibility, warehouse capacity monitoring, shipment awareness, supplier workflows, and procurement decision support through a transparent, explainable orchestration pipeline.

## Features

- Inventory Management
- Warehouse Capacity
- Shipment Tracking
- Supplier Management
- AI Procurement Assistant
- Multi-Tool Reasoning
- Planning Strategy
- Response Composer
- Explainable AI
- Enterprise Logging
- Custom Exceptions
- Unit Testing
- Swagger API
- Architecture Documentation

## Architecture

```mermaid
flowchart TD
    U[Frontend<br/>React + TypeScript + Vite] --> API[FastAPI API]
    API --> CHAT[AIChatService]
    CHAT --> COPILOT[CopilotTool]

    COPILOT --> ENGINE[ReasoningEngine]
    COPILOT --> COMPOSER[ResponseComposer]

    ENGINE --> PLANNER[ReasoningPlanner]
    PLANNER --> STRATEGY[PlanningStrategy]
    STRATEGY --> RULES[RuleBasedPlanner]
    RULES --> PLAN[ExecutionPlan]
    PLAN --> REGISTRY[ToolRegistry]

    REGISTRY --> INV[InventoryTool]
    REGISTRY --> WH[WarehouseTool]
    REGISTRY --> SHIP[ShipmentTool]
    REGISTRY --> PROC[ProcurementTool]

    INV --> DB[(PostgreSQL)]
    WH --> DB
    SHIP --> DB
    PROC --> DB

    ENGINE --> COMPOSER
    COMPOSER --> RESP[Natural Language Response]
    RESP --> U
```

## AI Reasoning Flow

```mermaid
sequenceDiagram
    actor User
    participant API as Chat API
    participant Planner as ReasoningPlanner
    participant Engine as ReasoningEngine
    participant Inventory as Inventory Tool
    participant Warehouse as Warehouse Tool
    participant Shipment as Shipment Tool
    participant Procurement as Procurement Tool
    participant Composer as ResponseComposer

    User->>API: Send procurement question
    API->>Engine: Forward user message
    Engine->>Planner: build_plan(message)
    Planner-->>Engine: ExecutionPlan
    Engine->>Inventory: run(...)
    Inventory-->>Engine: Inventory evidence
    Engine->>Warehouse: run(...)
    Warehouse-->>Engine: Capacity evidence
    Engine->>Shipment: run(...)
    Shipment-->>Engine: Shipment evidence
    Engine->>Procurement: run(...)
    Procurement-->>Engine: Procurement decision
    Engine->>Composer: compose(structured evidence)
    Composer-->>API: Formatted AI response
    API-->>User: Return Response
```

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic Settings |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Database | PostgreSQL |
| AI Layer | IntentEngine, ReasoningPlanner, PlanningStrategy, RuleBasedPlanner, ReasoningEngine, ToolRegistry, ResponseComposer |
| Testing | Pytest |
| Documentation | Markdown, Mermaid |

## Project Structure

Generated from the current repository layout:

```text
AI Clinical Supply Chain Copilot/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── planner/
│   │   │   ├── reasoning/
│   │   │   ├── response/
│   │   │   └── tools/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── docs/
│   │   └── architecture.md
│   └── tests/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── mock/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── router.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Installation

### Backend

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install the backend packages used by the current application:

```bash
pip install fastapi uvicorn sqlalchemy pydantic-settings pytest
```

If your `DATABASE_URL` requires a PostgreSQL driver, install the driver that matches your local setup.

### Frontend

```bash
cd frontend
npm install
```

### Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pharmachain
OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
```

### Database

1. Create a PostgreSQL database named `pharmachain`.
2. Update `DATABASE_URL` in `backend/.env`.
3. Start the backend application.
4. SQLAlchemy will create tables on startup through `Base.metadata.create_all(bind=engine)`.

## Running the Application

### Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

### Swagger

Open:

```text
http://localhost:8000/docs
```

### Tests

```bash
cd backend
python -m pytest
```

## AI Capabilities

### Intent Detection

PharmaChain uses a deterministic `IntentEngine` to classify incoming requests into inventory, warehouse, shipment, procurement, or unknown categories.

### Planning Strategy

`ReasoningPlanner` orchestrates planning by building a `PlannerContext` and delegating plan creation to a pluggable `PlanningStrategy`.

### Multi-Tool Reasoning

Procurement questions can trigger multi-step reasoning across inventory, warehouse, shipment, and procurement tools before a final response is produced.

### Tool Registry

`ToolRegistry` centralizes tool registration and lookup, keeping the execution layer decoupled from concrete tool implementations.

### Explainable AI

The reasoning pipeline preserves structured evidence including user request, planner reasoning, execution plan, and tool outputs for transparent decision support.

### Response Composition

`ResponseComposer` turns structured evidence into a professional natural-language recommendation with summary, confidence, and reasoning sections.

### Logging

The shared `PharmaChainAI` logger records incoming requests, plans, tool execution, durations, response composition, and failures using a consistent enterprise logging format.

### Unit Tests

The backend includes focused pytest coverage for planning, execution, registry behavior, response composition, and exception handling without requiring a database connection.

## Screenshots

### Dashboard

![Dashboard](assets/screenshots/dashboard.png)

### Inventory

![Inventory](assets/screenshots/inventory.png)

### Warehouse

![Warehouse](assets/screenshots/warehouse.png)

### Shipments

![Shipments](assets/screenshots/shipments.png)

### Procurement

![Procurement](assets/screenshots/procurement.png)

## Testing

Run the backend test suite with:

```bash
python -m pytest
```

The current project includes 12 passing unit tests covering the AI planning, execution, registry, and response composition layers.

## Documentation

Detailed architecture notes are available in:

- [`backend/docs/architecture.md`](backend/docs/architecture.md)

## Roadmap

### Completed

- FastAPI backend with Swagger documentation
- React + TypeScript frontend
- Inventory, warehouse, shipment, supplier, and procurement modules
- Rule-based AI planning
- Multi-tool reasoning engine
- Structured response composition
- Logging, exception handling, and backend unit tests

### Current Version

- Deterministic planning with `RuleBasedPlanner`
- Explainable procurement reasoning flow
- Portfolio-ready enterprise backend structure

### Future Versions

- Parallel Tool Execution
- LLM Planner
- Conversation Memory
- Workflow Graph Execution
- OpenAI Tool Calling
- Human-in-the-Loop Approval
- Observability Dashboard

## Why this project?

PharmaChain demonstrates how to build an enterprise-style AI system with practical software engineering discipline. It showcases:

- Enterprise Architecture
- Clean Architecture
- SOLID Principles
- Strategy Pattern
- Repository Pattern
- AI Orchestration
- Explainable AI
- Testing
- Observability
- Modern Python Development

## License

MIT

## Author

**Vibhuti Dhimar**  
Full Stack Software Engineer | AI Engineer  
Leicester, United Kingdom

- GitHub: [github.com/vibhutidhimar](https://github.com/vibhutidhimar)
- LinkedIn: [linkedin.com/in/vibhutidhimar](https://www.linkedin.com/in/vibhutidhimar)
