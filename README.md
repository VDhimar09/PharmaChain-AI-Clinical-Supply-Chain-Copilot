💊 PharmaChain -- AI Clinical Supply Chain Copilot
> AI-powered pharmaceutical supply chain platform built with **React,
> TypeScript, FastAPI, PostgreSQL and OpenAI**.
![Dashboard](assets/screenshots/dashboard.png)
🚀 Overview
PharmaChain is a full-stack AI Clinical Supply Chain Copilot designed to
help pharmaceutical organisations manage inventory, warehouse capacity,
shipments and AI-assisted procurement decisions from a single platform.
✨ Features
📊 Live Dashboard
📦 Inventory Management
🏭 Warehouse Capacity
🚚 Shipment Tracking
🤖 AI Procurement Copilot
📈 AI Insights
💬 Executive Copilot
🔐 JWT Authentication
🛡️ Role-Based Access Control (RBAC)
📸 Screenshots
Dashboard
![Dashboard](assets/screenshots/dashboard.png)
Inventory
![Inventory](assets/screenshots/inventory.png)
Warehouse Capacity
![Warehouse](assets/screenshots/warehouse-capacity.png)
Shipments
![Shipments](assets/screenshots/shipments.png)
AI Procurement
![AI Procurement](assets/screenshots/ai-procurement.png)
AI Insights
![AI Insights](assets/screenshots/ai-insights.png)
Executive Copilot
![Executive Copilot](assets/screenshots/executive-copilot.png)
🏗️ Architecture
``` text
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
SQLAlchemy
        │
PostgreSQL
        │
OpenAI / Azure OpenAI
```
⚙️ Tech Stack
Frontend
React
TypeScript
TanStack Router
Tailwind CSS
React Query
shadcn/ui
Backend
Python 3.13
FastAPI
SQLAlchemy
Alembic
PostgreSQL
AI
OpenAI
Azure OpenAI (supported)
Prompt Engineering
🔌 API Overview
Method   Endpoint
---
GET      /api/dashboard/summary
GET      /api/inventory
GET      /api/warehouse-zones
GET      /api/shipments
POST     /api/ai/procurement/analyze
GET      /api/ai/insights
POST     /api/ai/copilot/chat
🚀 Running Locally
``` bash
git clone https://github.com/VDhimar09/PharmaChain-AI-Clinical-Supply-Chain-Copilot.git
cd PharmaChain-AI-Clinical-Supply-Chain-Copilot
```
Backend
``` bash
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Frontend
``` bash
cd frontend
npm install
npm run dev
```
🌍 Environment Variables
Backend
``` env
DATABASE_URL=
JWT_SECRET_KEY=
OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
```
Frontend
``` env
VITE_API_BASE_URL=http://localhost:8000
```
🧪 Testing
``` bash
npm exec tsc --noEmit
npm run build
pytest
```
🗺️ Roadmap
Predictive demand forecasting
Supplier analytics
Notification centre
Export reports
Multi-warehouse optimisation
👩‍💻 Author
Vibhuti Dhimar
GitHub: https://github.com/VDhimar09
LinkedIn: https://www.linkedin.com/in/vibhutidhimar/
📄 License
MIT License.
