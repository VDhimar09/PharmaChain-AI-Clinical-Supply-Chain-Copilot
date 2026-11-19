# PharmaChain Frontend Instructions

## Technology

- React 19
- TypeScript 5
- Vite
- TanStack Router
- TanStack Query
- Tailwind CSS 4
- Zod

## Development Standards

1. Use functional React components and hooks.
2. Define explicit TypeScript types for component props, API payloads and responses.
3. Use interfaces and discriminated unions where appropriate.
4. Avoid `any` and loosely typed API responses.
5. Follow existing project structure and naming conventions.
6. Reuse components and avoid duplicated logic.
7. Keep components focused and maintainable.
8. Use Zod where runtime validation is required.
9. Keep frontend types aligned with backend API contracts.

## API Integration

- Follow existing API client conventions.
- Use the shared API client rather than duplicating fetch logic inside components.
- Attach Authorization headers only for authenticated requests.
- Follow existing token refresh, session and logout handling.
- Handle loading, success, empty and error states.
- Validate data at appropriate boundaries.
- Map backend errors into clear user-facing messages.
- Never expose backend secrets, API keys or credentials.
- Treat route parameters and user-controlled values as untrusted input.

## Authentication and Route Protection

- Follow existing authentication context and route-guard patterns.
- Use the established token storage and refresh mechanisms.
- Treat authentication tokens as sensitive client-side secrets.
- Never log tokens or expose them in UI messages.
- Do not rely on frontend permission checks as the only security control.
- Backend endpoints must enforce authentication and RBAC independently.
- Prevent protected pages from displaying sensitive data before authentication hydration completes.
- Handle expired sessions and refresh failures consistently.
- Redirect or fail closed when authentication cannot be established.

## TanStack Query

- Use TanStack Query for server-state management.
- Follow existing query and mutation hooks in the shared API hooks module.
- Use stable query keys scoped to the relevant entity and identifier.
- Use shared query functions instead of duplicating API requests.
- Configure `staleTime` and `gcTime` intentionally.
- Use `enabled` guards for optional identifiers and authenticated-user-dependent queries.
- Invalidate relevant queries after successful create, update or delete mutations.
- Avoid duplicate requests and inconsistent cached data.
- Follow existing authentication and cache-cleanup behaviour.

## Forms and User Experience

- Validate form input before submitting.
- Use Zod where appropriate for runtime validation.
- Avoid sending invalid payloads to the backend.
- Provide clear validation and server error messages.
- Handle loading, empty, success and retry states consistently.
- Use optimistic updates only when the resulting behaviour is safe and well-defined.
- Maintain responsive layouts.
- Preserve existing application behaviour.

## Accessibility

- Use semantic HTML elements.
- Provide accessible labels for all form fields and interactive controls.
- Give icon-only buttons accessible names.
- Use appropriate ARIA attributes such as `aria-label`, `aria-invalid` and `aria-describedby`.
- Support keyboard navigation.
- Preserve visible focus states.
- Manage focus appropriately after dialogs and important route transitions.
- Use accessible alerts for important errors and status messages.
- Do not rely on colour alone to communicate errors or status.

## Security and Sensitive Data

- Never embed API keys, credentials or backend secrets in browser-accessible code.
- Do not store unnecessary sensitive operational data in localStorage or sessionStorage.
- Never log authentication tokens or confidential user information.
- Treat URL parameters and client-submitted values as untrusted.
- Do not assume that hiding a UI control enforces backend permissions.
- Follow the existing session and logout security behaviour.

## AI and RAG User Interfaces

- Clearly distinguish retrieved evidence from AI-generated recommendations.
- Display supporting evidence and provenance where appropriate.
- Do not present unverified AI output as an authoritative operational decision.
- Require server-side approval and permission checks before operational actions.
- Do not expose internal prompts, raw tool outputs or restricted document sources.
- Clearly communicate when evidence is missing or insufficient.

## Quality Checks

Use the project's available scripts:

- `npm run lint`
- `npm exec tsc --noEmit`
- `npm run build`

Also consider:

- Checking important route and mutation flows.
- Verifying authentication and expired-session behaviour.
- Checking keyboard navigation and focus management.
- Reviewing loading, empty and error states.
- Checking responsive layouts.

Report exact commands and actual results. Do not claim success without evidence.

## AI Assistant Behaviour

- Inspect existing frontend components and hooks before making changes.
- Follow established project conventions.
- Prefer small, focused changes.
- Do not invent API behaviour or unsupported features.
- Explain important security or accessibility implications.
- Do not modify unrelated functionality without justification.

## Final Report

Summarise:

- Components and files affected.
- Frontend conventions followed.
- API and authentication considerations.
- Accessibility and security considerations.
- Validation performed.
- Exact commands and actual results.
- Remaining risks and recommendations.