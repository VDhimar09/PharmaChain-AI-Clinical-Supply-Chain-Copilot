<div align="center">

# 🏥 PharmaChain

### Enterprise AI Clinical Supply Chain Copilot

AI-powered operational intelligence for pharmaceutical inventory, warehouse capacity,
shipment monitoring and explainable procurement decision support.

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

Enterprise AI platform demonstrating modern backend engineering, explainable AI reasoning,
clean architecture and full-stack application development.

</div>

---

# 📖 Overview

PharmaChain is an enterprise-inspired AI Clinical Supply Chain platform that demonstrates how operational intelligence can support pharmaceutical inventory management, warehouse optimisation, shipment monitoring and procurement decision-making.

Unlike traditional chatbot demonstrations, PharmaChain uses a deterministic reasoning engine, planning strategy and modular tool orchestration to generate explainable recommendations backed by operational evidence.

---

# 🚀 Platform Overview

<p align="center">
<img src="assets/screenshots/dashboard.jpg" width="100%">
</p>

The Operations Dashboard provides a live command centre for pharmaceutical supply chain teams, surfacing inventory health, warehouse utilisation, shipment activity and AI-generated operational priorities.

---

# ✨ Core Modules

| Module | Description |
|---------|-------------|
| 📊 Dashboard | Executive operational overview |
| 📦 Inventory Intelligence | Monitor stock levels, expiry dates and shortages |
| 🏭 Warehouse Capacity | Capacity forecasting and utilisation monitoring |
| 🚚 Shipment Intelligence | Track inbound deliveries and shipment risks |
| 🤖 AI Procurement Copilot | Explainable procurement recommendations |
| 📈 AI Insights | Operational KPI summaries and critical alerts |
| 💬 Executive Copilot | Natural language operational assistant |
| 🔐 Security | JWT Authentication & Role-Based Access Control |

---

# 📸 Product Walkthrough

## 📊 Operations Dashboard

<p align="center">
<img src="assets/screenshots/dashboard.jpg" width="100%">
</p>

Provides a real-time operational overview of inventory, warehouse capacity, shipment activity and AI-prioritised actions.

---

## 📦 Inventory Intelligence

<p align="center">
<img src="assets/screenshots/inventory.jpg" width="100%">
</p>

Predict stock shortages before they impact operations while monitoring expiry dates, safety stock and temperature-controlled inventory.

---

## 🏭 Warehouse Capacity Planning

<p align="center">
<img src="assets/screenshots/warehouse-capacity.jpg" width="100%">
</p>

Forecast warehouse utilisation, identify capacity risks and recommend proactive inventory balancing.

---

## 🚚 Shipment Intelligence

<p align="center">
<img src="assets/screenshots/shipments.jpg" width="100%">
</p>

Track inbound deliveries, detect shipment delays and identify operational risks before they impact inventory.

---

## 🤖 AI Procurement Copilot

<p align="center">
<img src="assets/screenshots/ai-procurement.jpg" width="100%">
</p>

Uses explainable reasoning across inventory, warehouse capacity, incoming shipments and supplier reliability to recommend procurement decisions.

---

## 📈 AI Operational Insights

<p align="center">
<img src="assets/screenshots/ai-insights.jpg" width="100%">
</p>

Transforms operational data into executive summaries, KPIs and prioritised alerts generated directly from the backend.

---

## 💬 Executive Copilot

<p align="center">
<img src="assets/screenshots/executive-copilot.jpg" width="100%">
</p>

Allows operational teams to ask natural language questions while providing transparent evidence and reasoning behind every response.

---

# 🏗 System Architecture

```text
                    React Frontend
                           │
                    REST API (FastAPI)
                           │
               Authentication & RBAC
                           │
                 Reasoning Orchestrator
                           │
                    Planning Engine
                           │
                    Tool Registry
     ┌──────────────┬───────────────┬──────────────┐
     │              │               │              │
 Inventory      Warehouse       Shipment     Procurement
   Tool            Tool            Tool          Tool
     │              │               │              │
     └──────────────┴───────────────┴──────────────┘
                           │
                      PostgreSQL
```

---

# 🧠 AI Architecture

The platform demonstrates an explainable AI workflow built around deterministic planning rather than opaque responses.

**Workflow**

1. User submits a request
2. Intent Engine classifies the request
3. Planning Engine selects execution strategy
4. Tool Registry invokes the required operational services
5. Business rules validate the evidence
6. Response Composer generates an explainable recommendation

---

# ⚙ Technology Stack

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Pydantic
- JWT Authentication
- Role-Based Access Control (RBAC)

## Frontend

- React
- TypeScript
- Tailwind CSS
- TanStack Router

## AI Components

- Rule-Based Reasoning Engine
- Planning Engine
- Tool Registry
- Response Composer
- Operational Intelligence Engine

## Infrastructure

- Docker
- Git
- GitHub
- GitHub Actions
- Render
- Vercel

---

# 📂 Project Structure

```text
backend/
frontend/
assets/
 └── screenshots/
docs/
tests/
docker-compose.yml
README.md
```

---

# ⭐ Engineering Highlights

- Enterprise Clean Architecture
- Repository Pattern
- Service Layer
- Dependency Injection
- Strategy Pattern
- Modular AI Tool Registry
- Explainable Operational Intelligence
- RESTful APIs
- OpenAPI Documentation
- JWT Authentication
- RBAC Authorization
- Docker Support
- GitHub Actions CI/CD
- Unit Testing
- Integration Testing

---

# 🚀 Getting Started

```bash
git clone https://github.com/VDhimar09/pharmachain.git

cd pharmachain

docker compose up --build
```

Frontend

```
http://localhost:5173
```

Backend

```
http://localhost:8000
```

API Documentation

```
http://localhost:8000/docs
```

---

# 🗺 Roadmap

- ✅ Inventory Intelligence
- ✅ Warehouse Capacity Planning
- ✅ Shipment Intelligence
- ✅ AI Procurement Copilot
- ✅ AI Operational Insights
- ✅ Executive Copilot
- ✅ JWT Authentication
- ✅ Role-Based Access Control
- 🚧 OpenAI Integration
- 🚧 Retrieval-Augmented Generation (RAG)
- 🚧 Multi-Agent Workflows
- 🚧 Kubernetes Deployment
- 🚧 Observability & Monitoring

---

# 📄 License

This project is available under the MIT License.

---

<div align="center">

**Built by Vibhuti Dhimar**

AI Software Engineer • Product Engineer • NHS Tech Returner

</div>
