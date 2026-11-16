<!-- @format -->

# PharmaChain – GitHub Copilot Instructions

## 1. Project Overview

PharmaChain is an AI Clinical Supply Chain Copilot built using a React frontend and Python backend.

Before making changes, inspect the existing implementation and follow established project conventions.

Treat source code, dependency manifests and CI configuration as the source of truth when documentation conflicts.

## 2. Technology Stack

### Frontend

- React 19
- TypeScript 5
- Vite
- TanStack Router and TanStack Start
- TanStack Query
- Tailwind CSS 4
- Zod

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- PostgreSQL 16
- Alembic
- pgvector

### AI

- OpenAI API
- OpenAI embeddings
- Retrieval-Augmented Generation (RAG)
- Deterministic procurement reasoning

Do not assume technologies are actively implemented just because dependencies exist.

## 3. Backend Development Standards

- Follow existing router, service, repository and model separation.
- Use FastAPI conventions already established in the project.
- Use Pydantic v2 for request and response validation.
- Use SQLAlchemy 2.0 patterns.
- Keep business logic in appropriate service layers.
- Reuse existing dependencies and error-handling patterns.
- Avoid unnecessary architectural changes.

## 4. Frontend Development Standards

- Use TypeScript and preserve strict type checking.
- Follow existing TanStack file-based routing conventions.
- Reuse existing API clients, hooks and shared components.
- Use existing Tailwind CSS conventions.
- Avoid duplicating API logic.
- Preserve existing authentication and navigation behaviour.

## 5. Database Standards

- Use PostgreSQL-compatible SQLAlchemy models.
- Inspect existing Alembic migrations before schema changes.
- Understand existing startup table creation behaviour.
- Do not assume create_all replaces database migrations.
- Preserve UUID, JSONB and pgvector requirements.
- Never run destructive database operations against production data.

## 6. AI and Procurement Architecture

- Preserve deterministic procurement decision-making.
- Do not replace operational business rules with LLM-generated decisions.
- Maintain existing APPROVE, REJECT and REVIEW decision behaviour.
- Preserve temperature compatibility, warehouse capacity and incoming shipment checks.
- Keep RAG document retrieval and grounded generation separate from operational procurement decisions.
- Preserve evidence requirements and server-side citation validation.
- Do not claim LangGraph is fully implemented; inspect its actual implementation before extending it.

## 7. Security and Privacy

- Preserve authentication, JWT and refresh-token handling.
- Respect existing role-based access control and permission checks.
- Never expose secrets, credentials or tokens.
- Avoid logging sensitive prompts, document contents or unnecessary personal information.
- Preserve document upload validation and citation security.
- Never introduce development credentials into production configuration.
- Do not claim HIPAA, GxP, FDA or other regulatory compliance without verified evidence.

## 8. Testing and Validation

### Backend

- Follow existing pytest conventions.
- Inspect fixtures and test configuration before adding tests.
- Backend tests require an isolated PostgreSQL/pgvector test database.
- Never run tests against an unknown or production database.
- Run targeted tests before the full suite.

### Frontend

Use existing project scripts:

- `npm run lint`
- `npm exec tsc --noEmit`
- `npm run build`

Do not assume a frontend automated test suite exists.

### CI

- Preserve existing backend CI requirements.
- Check the GitHub Actions workflow before changing dependencies or Docker configuration.
- Do not claim a command passed unless it was actually executed successfully.

## 9. Development Workflow

Before making changes:

1. Inspect relevant files.
2. Understand existing implementation.
3. Identify the smallest appropriate change.
4. Explain the proposed approach.

When implementing:

- Avoid unrelated modifications.
- Preserve existing working functionality.
- Reuse existing patterns.
- Add or update relevant tests.
- Avoid unnecessary dependencies.

After implementation:

1. Run appropriate validation.
2. Review the changes.
3. Report modified files.
4. Report exact commands and results.
5. Clearly identify unresolved issues.

## 10. AI Coding Assistant Behaviour

- Do not invent files, functions, APIs or architecture.
- Ask before making broad or destructive changes.
- Do not modify unrelated application code.
- Prefer small, reviewable changes.
- Explain important technical decisions clearly.
- Distinguish verified facts from assumptions.
- Never claim implementation or testing is complete without evidence.
