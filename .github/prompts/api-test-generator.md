<!-- @format -->

# API Test Generator

## Purpose

Generate meaningful automated tests for PharmaChain FastAPI endpoints.

## Instructions

1. Inspect the endpoint, service, schema and repository.
2. Review existing tests and fixtures.
3. Identify missing test scenarios.
4. Follow existing pytest conventions.
5. Reuse fixtures where appropriate.
6. Do not invent expected behaviour.

## Coverage

Consider:

- Successful requests.
- Missing or invalid fields.
- Boundary values.
- Authentication and authorization.
- Missing records.
- Business-rule failures.
- Response validation.

## Safety

- Never use a production database.
- Do not expose credentials or sensitive data.
- Do not modify application code unless requested.

## Validation

Report exact commands and actual test results.
Never claim tests passed without evidence.

## Final Report

Summarise test scenarios, files changed, execution results and remaining gaps.
