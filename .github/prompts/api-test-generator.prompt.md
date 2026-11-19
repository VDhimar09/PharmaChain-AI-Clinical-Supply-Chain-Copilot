<!-- @format -->

---

name: API Test Generator
description: Generate reliable FastAPI endpoint tests following PharmaChain's existing pytest conventions.

---

# PharmaChain API Test Generator

You are helping develop and test the PharmaChain FastAPI backend.

## Objective

Generate or improve automated tests for the specified API endpoint.

## Instructions

1. Inspect the endpoint implementation before writing tests.
2. Inspect its related service, schemas, dependencies and existing tests.
3. Read `backend/tests/conftest.py` and reuse existing fixtures.
4. Follow the existing pytest and FastAPI TestClient conventions.
5. Do not invent endpoints, fixtures, models or expected behaviour.

## Test coverage

Consider relevant scenarios:

- Successful requests.
- Missing or invalid request fields.
- Boundary values.
- Missing database records.
- Authentication and authorization failures.
- Relevant business-rule failures.
- Expected error responses.

Only include scenarios applicable to the actual endpoint.

## Safety

- Never use a production database.
- Use the established isolated PostgreSQL/pgvector test environment.
- Do not expose credentials or personal data.
- Do not weaken authentication or validation.
- Do not modify application code unless explicitly requested.

## Validation

1. Start with the narrowest relevant pytest target.
2. Report the exact command executed.
3. Report passed, failed and skipped tests.
4. Explain any environment limitations.
5. Never claim tests passed without observing successful results.

## Final report

Summarise:

- Endpoint tested.
- Test scenarios added.
- Files created or modified.
- Test execution results.
- Remaining gaps.
