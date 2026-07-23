# 💊 PharmaChain – AI Clinical Supply Chain Copilot

> An AI-powered Clinical Supply Chain Copilot that helps pharmaceutical organisations monitor inventory, optimise warehouse operations, analyse procurement requests, and support operational decision-making using intelligent workflows.

---

## Overview

PharmaChain is a full-stack AI application designed to improve visibility across pharmaceutical supply chain operations.

The platform combines operational dashboards with AI-powered decision support to help warehouse managers, procurement teams and supply chain planners monitor inventory, warehouse utilisation, shipments and procurement activities from a single interface.

Unlike a traditional dashboard, PharmaChain includes AI-driven capabilities that explain decisions, present supporting evidence and recommend actions based on live operational data.

---

## Business Problem

Clinical supply chains manage products with strict regulatory and operational requirements.

Teams often work across multiple systems to answer questions such as:

- Which products are running low?
- Which warehouse zones are nearing capacity?
- Which shipments are delayed?
- Should this procurement request be approved?
- What operational risks require immediate attention?

PharmaChain brings these answers together into a single AI-assisted platform.

---

# Key Features

## 📊 Operational Dashboard

- Live inventory overview
- Warehouse occupancy
- Shipment monitoring
- Today's operational priorities
- Cold-chain warehouse visibility

---

## 📦 Inventory Management

- Live inventory records
- Low stock monitoring
- Healthy SKU tracking
- Expiring product visibility
- Product search and filtering

---

## 🏭 Warehouse Management

- Warehouse capacity monitoring
- Zone utilisation
- Available capacity
- Occupancy analysis
- Cold-chain support

---

## 🚚 Shipment Management

- Live shipment tracking
- In Transit monitoring
- Delivered shipments
- Delayed shipments
- Processing shipments
- Search and filtering

---

## 🤖 AI Procurement Copilot

Analyse procurement requests using deterministic AI workflows.

The AI evaluates:

- Inventory availability
- Warehouse capacity
- Temperature compatibility
- Supplier information
- Incoming shipments
- Procurement justification

Returns:

- Approve
- Review
- Reject

with detailed reasoning and supporting evidence.

---

## 📈 AI Insights

Executive operational insights generated from live backend data.

Includes:

- Executive summary
- Inventory health
- Warehouse insights
- Shipment insights
- Procurement insights
- Alerts
- Recommendations
- Trend summaries

---

## 💬 Executive Copilot

Natural language operational assistant.

Example questions:

> Show delayed shipments.

> Which warehouse is nearly full?

> Why was this procurement request rejected?

> What should operations prioritise today?

Responses include:

- Decision reasoning
- Tool execution timeline
- Supporting evidence
- Confidence level
- Recommendations

---

# Architecture

```
                    React + TypeScript
                            │
                     TanStack Router
                            │
                      React Query
                            │
────────────────────────────────────────────────
                     FastAPI Backend
────────────────────────────────────────────────
                            │
                    Business Services
                            │
                    SQLAlchemy ORM
                            │
                      PostgreSQL
                            │
                 OpenAI / Azure OpenAI
```

---

# Technology Stack

## Frontend

- React
- TypeScript
- TanStack Router
- React Query
- Tailwind CSS
- shadcn/ui
- Recharts
- Lucide Icons

---

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL

---

## AI

- OpenAI
- Azure OpenAI (supported)
- Prompt Engineering
- Tool Calling
- Deterministic AI Workflows

---

## Security

- JWT Authentication
- Refresh Tokens
- Role-Based Access Control (RBAC)
- Password Hashing
- Protected API Endpoints

---

# Application Architecture

```
Frontend
│
├── Dashboard
├── Inventory
├── Warehouse
├── Shipments
├── AI Procurement
├── AI Insights
└── Executive Copilot

            │

React Query API Layer

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
```

---

# Project Structure

```
PharmaChain
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── routes/
│   └── lib/
│
├── backend/
│   ├── app/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   └── core/
│
└── docs/
```

---

# Backend APIs

Examples include:

```
GET    /api/dashboard/summary

GET    /api/inventory

GET    /api/warehouse-zones

GET    /api/shipments

POST   /api/ai/procurement/analyze

GET    /api/ai/insights

POST   /api/ai/copilot/chat
```

---

# Authentication

The application includes:

- JWT Access Tokens
- Refresh Tokens
- Login
- Logout
- Current User endpoint
- Role-Based Access Control
- Protected API routes

---

# Screenshots

> Add screenshots here.

Dashboard

Inventory

Warehouse

Shipments

AI Procurement

AI Insights

Executive Copilot

---

# Running Locally

## Backend

```bash
cd backend

python -m venv .venv

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Environment Variables

Backend

```env
DATABASE_URL=

JWT_SECRET_KEY=

OPENAI_API_KEY=

AZURE_OPENAI_ENDPOINT=

AZURE_OPENAI_API_KEY=
```

Frontend

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

# Future Enhancements

- Predictive demand forecasting
- AI anomaly detection
- Supplier performance analytics
- Interactive warehouse heatmaps
- Notification centre
- Export to PDF / Excel
- Multi-warehouse optimisation
- Advanced reporting

---

# Author

**Vibhuti Dhimar**

Software Engineer | AI Engineer | Product Builder

- GitHub: https://github.com/VDhimar09
- LinkedIn: https://www.linkedin.com/in/vibhutidhimar/

---

# License

This project is licensed under the MIT License.
