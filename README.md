
# 💊 PharmaChain – AI Clinical Supply Chain Copilot

<p align="center">
  <strong>AI-powered pharmaceutical supply chain platform built with React, FastAPI, PostgreSQL and OpenAI.</strong>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)
![React](https://img.shields.io/badge/React-19-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791)
![OpenAI](https://img.shields.io/badge/OpenAI-AI-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

</p>

---

## 📖 Overview

PharmaChain is a full-stack AI-powered Clinical Supply Chain Copilot designed to help pharmaceutical organisations monitor inventory, warehouse capacity, shipments and procurement decisions from a single intelligent platform.

The application combines operational dashboards with AI-assisted workflows, giving supply chain teams actionable insights supported by live backend data.

---

# ✨ Features

- 📊 Live Operational Dashboard
- 📦 Inventory Management
- 🏭 Warehouse Capacity Monitoring
- 🚚 Shipment Tracking
- 🤖 AI Procurement Analysis
- 📈 AI Insights Dashboard
- 💬 Executive Copilot
- 🔐 JWT Authentication
- 🛡️ Role-Based Access Control (RBAC)

---

# 📸 Screenshots

> Place these images inside `docs/images/`

## Dashboard

![Dashboard](docs/images/dashboard.png)

## Inventory

![Inventory](docs/images/inventory.png)

## Warehouse Capacity

![Warehouse](docs/images/warehouse-capacity.png)

## Shipments

![Shipments](docs/images/shipments.png)

## AI Procurement

![AI Procurement](docs/images/ai-procurement.png)

## AI Insights

![AI Insights](docs/images/ai-insights.png)

## Executive Copilot

![Executive Copilot](docs/images/executive-copilot.png)

---

# 🏗️ Architecture

```text
React + TypeScript
        │
TanStack Router
        │
React Query
        │
FastAPI
        │
Business Services
        │
Repositories
        │
SQLAlchemy
        │
PostgreSQL
        │
OpenAI / Azure OpenAI
```

---

# 🤖 AI Capabilities

## AI Procurement

Evaluates procurement requests using live operational data.

Checks:

- Inventory availability
- Supplier information
- Warehouse capacity
- Temperature compatibility
- Incoming shipments

Returns:

- Approve
- Review
- Reject

with reasoning and evidence.

---

## AI Insights

Provides:

- Executive Summary
- Inventory Health
- Warehouse Insights
- Shipment Insights
- Procurement Insights
- Alerts
- Recommendations

---

## Executive Copilot

Natural language assistant capable of answering operational questions using backend tools and AI reasoning.

Example prompts:

- Show delayed shipments
- Which warehouse is nearly full?
- Which products are running low?
- Why was this procurement request rejected?

---

# ⚙️ Technology Stack

## Frontend

- React
- TypeScript
- TanStack Router
- React Query
- Tailwind CSS
- shadcn/ui
- Recharts

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL

## AI

- OpenAI
- Azure OpenAI (supported)
- Prompt Engineering

---

# 🔐 Security

- JWT Authentication
- Refresh Tokens
- RBAC
- Protected Routes
- Password Hashing

---

# 📁 Project Structure

```text
PharmaChain
│
├── frontend/
├── backend/
├── docs/
│   └── images/
├── README.md
└── LICENSE
```

---

# 🔌 API Overview

| Method | Endpoint | Purpose |
|---------|----------|---------|
| GET | /api/dashboard/summary | Dashboard KPIs |
| GET | /api/inventory | Inventory |
| GET | /api/warehouse-zones | Warehouse |
| GET | /api/shipments | Shipments |
| POST | /api/ai/procurement/analyze | AI Procurement |
| GET | /api/ai/insights | AI Insights |
| POST | /api/ai/copilot/chat | Executive Copilot |

---

# 🚀 Getting Started

## Clone

```bash
git clone https://github.com/VDhimar09/PharmaChain-AI-Clinical-Supply-Chain-Copilot.git
cd PharmaChain-AI-Clinical-Supply-Chain-Copilot
```

## Backend

```bash
cd backend

python -m venv .venv

pip install -r requirements.txt

uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🌍 Environment Variables

Backend:

```env
DATABASE_URL=
JWT_SECRET_KEY=
OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
```

Frontend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

# 🧪 Testing

Frontend

```bash
npm exec tsc --noEmit
npm run build
```

Backend

```bash
pytest
```

---

# 🛣️ Roadmap

- Predictive demand forecasting
- Supplier analytics
- Notification centre
- Export reports
- Warehouse heatmaps
- Multi-site optimisation

---

# 👩‍💻 Author

**Vibhuti Dhimar**

Software Engineer | AI Engineer | Product Builder

GitHub: https://github.com/VDhimar09

LinkedIn: https://www.linkedin.com/in/vibhutidhimar/

---

# 📄 License

This project is licensed under the MIT License.

---

## ⭐ Project Highlights

- Live frontend integrated with FastAPI backend
- AI Procurement workflow
- AI Insights dashboard
- Executive Copilot
- JWT Authentication & RBAC
- PostgreSQL persistence
- React Query data layer
- TypeScript frontend
- Modular service architecture

If you found this project interesting, please consider giving it a ⭐ on GitHub.
