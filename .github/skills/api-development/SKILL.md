---
name: api-development
description: Develop and review PharmaChain FastAPI endpoints using established backend conventions, secure database practices, RBAC and testing standards.
---

# PharmaChain API Development Skill

## Purpose
Guide developers when creating, modifying or reviewing FastAPI endpoints in PharmaChain.

## Instructions
1. Inspect existing routes, services, schemas and repositories before making changes.
2. Follow existing API, dependency-injection and router-registration conventions.
3. Use Pydantic schemas for request and response validation.
4. Define appropriate field constraints, formats, required values and boundary conditions.
5. Keep business logic in services rather than route handlers.
6. Use repositories for database access.
7. Apply appropriate authentication and server-side RBAC permissions.
8. Handle expected domain errors consistently.
9. Do not silently hide unexpected database or downstream failures.
10. Avoid unnecessary changes to unrelated functionality.

## Database Safety
- Use SQLAlchemy conventions already established in the project.
- Use Alembic for schema migrations and deployed database schema evolution.
- Do not treat `Base.metadata.create_all()` as a replacement for Alembic migrations.
- Inspect application startup and database initialisation behaviour before running tests.
- Never run tests against production or an unverified database.
- Use a disposable, isolated test database for database integration tests.
- Verify the test database connection and configuration before executing tests.
- Be aware that importing the application may trigger database setup or other startup side effects.
- Protect existing data and never perform destructive operations against an unverified database.

## Security and Permissions
- Never expose credentials, passwords, tokens or secrets.
- Validate user input on the server.
- Enforce authentication and RBAC permissions on protected endpoints.
- Do not rely on frontend permission checks.
- Distinguish between permissions to create, review, approve and execute operational actions.
- Do not allow users to bypass approval workflows through unrestricted request fields.
- Avoid logging sensitive information, credentials or confidential document content.

## API and Business Logic
- Keep route handlers focused on HTTP concerns.
- Delegate business rules to service classes.
- Use repositories for database queries and persistence.
- Return appropriate HTTP status codes and response schemas.
- Define expected error mappings for validation, missing records and business-rule failures.
- Translate known domain exceptions into appropriate API responses.
- Preserve visibility of unexpected failures rather than swallowing exceptions or returning misleading success responses.
- Confirm that every accepted request field has a defined purpose and affects behaviour as intended.
- Avoid introducing duplicate database operations unnecessarily.

## AI and Decision-Making Endpoints
- Clearly distinguish deterministic business rules from LLM-generated content.
- Do not replace deterministic procurement decisions with unverified LLM output.
- Keep recommendations separate from authorised operational state changes.
- Require appropriate permissions and an auditable workflow before recommendations can trigger operational actions.
- Validate AI-generated responses and citations where applicable.
- Use a defined fallback when reliable supporting evidence is unavailable.
- Do not claim an AI decision is reliable without appropriate evidence and validation.

## Testing
Follow existing PharmaChain pytest and FastAPI TestClient conventions. Consider successful requests, invalid and boundary values, authentication and authorization failures, missing records, business-rule failures, response validation, audit events, approval boundaries and database query behaviour.

- Reuse existing fixtures and project conventions.
- Use service monkeypatching for route tests where appropriate.
- Use stub collaborators for isolated service tests where appropriate.
- Use isolated database tests when repository queries or database behaviour need verification.
- Never assume that a test passed without checking its actual output.
- Do not claim integration tests passed if database setup prevented execution.

## Final Report
Summarise endpoint changes, files affected, architecture and conventions followed, security and permission considerations, validation performed, exact test commands and actual results, tests not executed and reasons, and remaining risks.
