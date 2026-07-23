🏥 PharmaChain
Enterprise AI Clinical Supply Chain Copilot
> **AI-powered operational intelligence platform for pharmaceutical inventory, warehouse management, shipment monitoring and explainable procurement decision support.**
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
---
📖 Overview
PharmaChain is an enterprise-inspired AI platform demonstrating how modern software engineering and explainable AI can support pharmaceutical supply chain operations.
The platform combines FastAPI, React, PostgreSQL and a modular AI reasoning engine to provide operational visibility across inventory, warehousing, procurement and logistics.
🎯 Key Features
📊 Executive Operations Dashboard
📦 Inventory Intelligence
🏭 Warehouse Capacity Planning
🚚 Shipment Intelligence
🤖 AI Procurement Copilot
📈 AI Operational Insights
💬 Executive AI Copilot
🔐 JWT Authentication
🛡️ Role-Based Access Control (RBAC)
🐳 Docker Ready
---
📸 Product Overview
Executive Dashboard
<p align="center">
<img src="assets/screenshots/dashboard.jpg" width="100%">
</p>
Real-time operational overview with KPIs, inventory health, warehouse utilisation and AI-generated recommendations.
---
Inventory Intelligence
<p align="center">
<img src="assets/screenshots/inventory.jpg" width="100%">
</p>
Monitor stock levels, expiry dates, low-stock alerts and product availability.
---
Warehouse Capacity Planning
<p align="center">
<img src="assets/screenshots/warehouse-capacity.jpg" width="100%">
</p>
Forecast warehouse occupancy and optimise storage utilisation.
---
Shipment Intelligence
<p align="center">
<img src="assets/screenshots/shipments.jpg" width="100%">
</p>
Track inbound deliveries and identify shipment risks.
---
AI Procurement Copilot
<p align="center">
<img src="assets/screenshots/ai-procurement.jpg" width="100%">
</p>
Generate explainable procurement recommendations using inventory, warehouse and shipment evidence.
---
AI Operational Insights
<p align="center">
<img src="assets/screenshots/ai-insights.jpg" width="100%">
</p>
Executive summaries and operational intelligence generated from backend data.
---
Executive AI Copilot
<p align="center">
<img src="assets/screenshots/executive-copilot.jpg" width="100%">
</p>
Natural language operational assistant with explainable responses.
---
🏗️ System Architecture
```text
React Frontend
      │
 FastAPI REST API
      │
 Authentication & RBAC
      │
 AI Reasoning Engine
      │
 Planning Engine
      │
 Tool Registry
 ├── Inventory Tool
 ├── Warehouse Tool
 ├── Shipment Tool
 └── Procurement Tool
      │
 PostgreSQL
```
AI Workflow
```text
User Request
     │
Intent Detection
     │
Planning Engine
     │
Tool Selection
     │
Business Rules
     │
Evidence Collection
     │
Response Composer
     │
Explainable Recommendation
```
---
🛠️ Technology Stack
Backend
Python 3.13
FastAPI
SQLAlchemy
PostgreSQL
Alembic
Pydantic
JWT Authentication
Frontend
React
TypeScript
Tailwind CSS
AI
Rule-Based Reasoning
Planning Engine
Tool Registry
Response Composer
DevOps
Docker
GitHub Actions
Render
Vercel
---
📂 Project Structure
```text
backend/
frontend/
assets/
└── screenshots/
docs/
tests/
README.md
docker-compose.yml
```
---
🚀 Getting Started
Clone
```bash
git clone https://github.com/VDhimar09/PharmaChain-AI-Clinical-Supply-Chain-Copilot.git
cd PharmaChain-AI-Clinical-Supply-Chain-Copilot
```
Backend
```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Frontend
```bash
cd frontend
npm install
npm run dev
```
Docker
```bash
docker compose up --build
```
---
🌐 Local URLs
Service	URL
Frontend	http://localhost:5173
Backend	http://localhost:8000
API Docs	http://localhost:8000/docs
---
🔐 Security
JWT Authentication
Refresh Tokens
Password Hashing
RBAC
Protected API Endpoints
---
🧪 Testing
```bash
pytest
```
---
🗺️ Roadmap
Completed
Dashboard
Inventory Intelligence
Warehouse Capacity
Shipment Intelligence
AI Procurement Copilot
AI Operational Insights
Executive Copilot
JWT Authentication
RBAC
Planned
OpenAI Integration
Azure OpenAI
Retrieval-Augmented Generation (RAG)
Redis
Kubernetes
Monitoring & Observability
---
👩‍💻 Author
Vibhuti Dhimar
AI Software Engineer • Product Engineer • NHS Tech Returner
This project showcases enterprise software engineering principles, explainable AI and full-stack development through a realistic pharmaceutical supply chain platform.
---
📄 License
Licensed under the MIT License.
