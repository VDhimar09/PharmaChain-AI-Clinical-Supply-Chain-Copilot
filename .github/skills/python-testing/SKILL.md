---
name: python-testing
description: Create, improve, and validate Python tests in PharmaChain. Use when adding or changing Python backend code, FastAPI endpoints, services, database operations, Pydantic validation, or when investigating a test failure.
---

# Python Testing Skill

## Purpose

Produce reliable, maintainable tests for the PharmaChain Python backend. Tests must reflect the existing implementation and project conventions; never assume an endpoint, model, fixture, or behaviour exists without checking the repository.

## Project context

The backend uses Python, FastAPI, SQLAlchemy 2.0, Pydantic v2, and PostgreSQL. The test framework is pytest where configured. Before writing tests, inspect the backend test configuration, existing tests, application structure, fixtures, and dependency overrides.

## Workflow

1. **Inspect before changing**
   - Read the production code and related tests.
   - Identify the public behaviour, dependencies, side effects, and failure modes.
   - Check pytest configuration, installed test dependencies, fixtures, and test database setup.
   - Reuse established naming, imports, fixtures, and patterns.

2. **Choose the right test level**
   - Unit tests for isolated functions and service logic.
   - API tests for FastAPI routes, request/response schemas, status codes, and dependency behaviour.
   - Database integration tests only when the repository provides a safe test database or established isolated database fixture.
   - Do not connect tests to production or a developer's live database.

3. **Cover meaningful behaviour**
   - Typical successful inputs and expected results.
   - Missing, malformed, and boundary inputs.
   - Not-found and conflict conditions where applicable.
   - Permission/authorization failures where applicable.
   - Database and external-service failures where relevant.
   - Regression cases for the reported defect.

4. **Keep tests deterministic**
   - Use fixtures for setup and cleanup.
   - Mock external APIs, cloud services, clocks, and other nondeterministic boundaries when appropriate.
   - Prefer FastAPI dependency overrides for dependencies that need isolation.
   - Avoid sleeps, real network calls, shared mutable state, and order-dependent tests.
   - Use realistic values, but never include credentials, personal data, or production records.

5. **Assert observable outcomes**
   - Check return values, response status and payload, persisted state, and relevant side effects.
   - Assert meaningful details rather than merely checking that code did not raise.
   - Keep each test focused on one behaviour.

6. **Run and review**
   - Run the narrowest relevant pytest target first, then the broader backend suite when practical.
   - Use the project's documented command and environment.
   - Review failures; distinguish test defects, environment/configuration problems, and production defects.
   - Do not change production code merely to make a test pass without understanding the cause.
   - Do not claim tests passed unless the command completed successfully and the result was observed.

7. **Report**
   - Summarise files changed and behaviours covered.
   - Include the exact test command and pass/fail result.
   - List failures, skipped tests, environmental limitations, and remaining risks honestly.

## Technology-specific guidance

### FastAPI
- Use the existing TestClient or async client convention from the repository.
- Exercise route behaviour through the public HTTP interface where appropriate.
- Override authentication, database, and other dependencies using the application's established mechanisms.
- Check status codes and response bodies, including validation and error responses.
- Restore or clear overrides after each test.

### Services and business logic
- Test service behaviour independently of HTTP where possible.
- Cover normal results, boundary conditions, and expected exceptions.
- Mock collaborators at the boundary where they are used; avoid mocking the function under test.

### SQLAlchemy 2.0 and PostgreSQL
- Follow the repository's existing session and transaction fixtures.
- Isolate test data and clean up reliably.
- Test persistence and query behaviour against the configured test database when integration testing is supported.
- Do not assume SQLite is equivalent to PostgreSQL for dialect-specific behaviour.
- Never run destructive setup or cleanup against a production database.

### Pydantic v2
- Test valid model construction and serialisation.
- Test invalid values, missing required fields, and relevant constraints.
- Assert useful validation details without coupling unnecessarily to unstable error-message wording.

## Example test shape

Use this only as a pattern; adapt imports, fixtures, and expected behaviour to actual project code.

```python
def test_service_returns_expected_result(service):
    result = service.perform_action(valid_input)

    assert result.status == "success"
    assert result.value == expected_value
```

## Safety and scope

- Do not expose secrets or copy values from environment files into tests.
- Do not weaken validation, authorization, or security controls to satisfy tests.
- Do not invent application behaviour or fixtures.
- Do not make unrelated production changes.
- Ask for missing information only when it blocks a safe, correct test.
