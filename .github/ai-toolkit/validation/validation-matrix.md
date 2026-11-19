# AI Toolkit Validation Matrix

## Purpose

Track the quality, testing and maintenance of reusable AI development resources.

| Resource | Validation Scenario | Status | Evidence |
|---|---|---|---|
| Python Testing skill | Generate and review backend tests | Tested | PharmaChain procurement tests |
| Project instructions | Check Copilot follows project rules | Validated | Copilot architecture questions |
| API Test Generator | Generate procurement API test plan | Tested | Copilot test plan |
| Bug Investigation | Investigate inventory HTTP 500 | Tested | Investigation report |
| PR Review prompt | Review PharmaChain test changes | Tested | Copilot reviewed Git diff and reported severity, evidence and follow-up tests |
| Code Reviewer agent | Review procurement test changes | Tested | Review findings |
| Test Engineer agent | Investigate approval permission risk | Tested | Proposed test scenarios |
| Architecture Reviewer agent | Review procurement architecture | Tested | Architecture report |
| Frontend instructions | Validate frontend guidance | Pending | Not yet tested |
| API Development skill | Review API development guidance against PharmaChain | Tested | Two Copilot reviews; improvements identified |
| Backend instructions | Review security, authentication, database and RAG guidance | Validated | Two Copilot reviews against backend implementation |

## Validation Status Definitions

- **Pending:** Resource has been created but not yet tested.
- **Tested:** Resource has been exercised in a relevant scenario.
- **Validated:** Behaviour has been reviewed against project requirements.
- **Failed:** Testing identified an issue requiring correction.

A resource marked Tested or Validated does not automatically mean that all generated code or related project tests passed.

## Validation Criteria

Evaluate each resource for:

1. Accuracy.
2. Relevance to the task.
3. Consistency with project conventions.
4. Security awareness.
5. Quality of recommendations.
6. Evidence supporting conclusions.

## Maintenance

- Re-test resources after significant changes.
- Update documentation when guidance becomes outdated.
- Record improvements and validation evidence.
- Never mark a resource as tested without evidence.

## Known Validation Limitations

- Backend integration tests have not yet completed successfully because the isolated PostgreSQL test environment was unavailable.
- Static checks such as `py_compile` and `git diff --check` succeeded, but they do not prove integration tests pass.
- Architecture findings require independent verification before implementation.
- The shared AI Toolkit under `.github/ai-toolkit/` is the central documentation and resource library.
- Active GitHub Copilot integrations remain in their respective `.github/skills/`, `.github/prompts/`, `.github/agents/` and instruction files.
- Changes to shared library copies must be reflected in the active integration files when applicable.