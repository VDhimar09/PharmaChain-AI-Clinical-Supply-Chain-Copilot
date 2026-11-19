# PharmaChain Backend Instructions

## Technology

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- PostgreSQL 16
- Alembic
- Pytest
- pgvector for vector search and document embeddings

## Development Standards

1. Keep route handlers focused on HTTP concerns.
2. Put business logic in service classes.
3. Use repositories for database access.
4. Use Pydantic schemas for request and response validation.
5. Follow existing dependency-injection patterns.
6. Use type hints and clear error handling.
7. Inspect existing implementations before introducing new patterns.
8. Keep changes focused and avoid unrelated modifications.

## Database

- Use established SQLAlchemy conventions.
- Manage deployed schema changes through Alembic migrations.
- Do not treat `Base.metadata.create_all()` as a replacement for Alembic migrations.
- Verify that the PostgreSQL `vector` extension is available before creating or migrating vector columns.
- Follow existing pgvector conventions for embedding storage and similarity queries.
- Protect existing data.
- Never run tests against production or an unverified database.
- Use a disposable, isolated test database for database integration tests.
- Verify database configuration before executing destructive operations.
- Be aware that importing `app.main` can trigger database extension and table initialisation.

## Security and Authentication

- Enforce authentication and server-side RBAC permissions.
- Use existing `Depends(require_permission(...))` and `Depends(require_role(...))` patterns where appropriate.
- Validate bearer access tokens and their expected token type.
- Reject invalid tokens, invalid subjects and inactive users.
- Follow existing refresh-token rotation and revocation mechanisms.
- Store refresh-token hashes rather than raw refresh tokens.
- Never trust client-supplied actor identity, approval status or AI provenance.
- Derive user identity and sensitive operational fields from trusted server-side logic.
- Treat default JWT secrets and bootstrap administrator credentials as development-only values.
- Override default credentials using secure environment configuration or secret management before deployment.
- Never commit real credentials, tokens or secrets.
- Restrict CORS origins to explicitly trusted frontend origins.
- Validate incoming data on the server.

## Logging and Data Protection

- Never log credentials, passwords, authentication tokens or refresh tokens.
- Avoid logging raw request bodies containing sensitive information.
- Do not expose document chunk text or embedding vectors in production logs.
- Keep SQL statement logging disabled outside development.
- Avoid exposing confidential clinical, supplier or operational information in logs.
- Follow existing application logging and error-handling conventions.

## Document Ingestion and RAG

- Enforce configured upload-size limits.
- Validate permitted MIME types and file extensions.
- Follow existing document sanitisation and storage-provider conventions.
- Preserve the configured document chunking strategy.
- Protect document content and embeddings.
- Ground generated responses in retrieved evidence.
- Validate citations against retrieved source documents before returning them.
- Use defined fallbacks when evidence is unavailable.
- Do not produce affirmative recommendations when evidence is insufficient.
- Clearly distinguish missing evidence from verified evidence.

## AI and Procurement

- Keep procurement decisions deterministic.
- Do not replace established business rules with unsupported LLM decisions.
- Keep AI recommendations separate from authorised operational actions.
- Require appropriate permissions and auditable workflows before approval or execution.
- Ensure accepted request fields have a defined purpose and influence behaviour as intended.
- Validate AI-generated content and evidence before returning results.

## Testing

- Follow existing pytest and FastAPI TestClient conventions.
- Test success, validation boundaries, permissions, missing records and business-rule failures.
- Test authentication and refresh-token behaviour where relevant.
- Test audit events and expected database side effects.
- Use isolated databases for database integration tests.
- Do not copy unsafe test patterns, such as deleting entire tables without verified test-database isolation.
- Use appropriate mocks or stubs for isolated service and route tests.
- Report actual test results and exact commands.
- Clearly identify tests that could not run and explain why.
- Never claim tests passed without evidence.

## AI Assistant Behaviour

- Inspect existing code before suggesting changes.
- Prefer small, focused changes.
- Do not invent project functionality or claim unverified implementation details.
- Explain security implications before suggesting risky operations.
- Ask before making destructive database or infrastructure changes.
- Clearly distinguish confirmed findings from assumptions and recommendations.

## Final Report

Summarise:

- Files and components affected.
- Architecture and conventions followed.
- Security and database considerations.
- Validation performed.
- Exact test commands and actual results.
- Tests not executed and reasons.
- Remaining risks and recommendations.