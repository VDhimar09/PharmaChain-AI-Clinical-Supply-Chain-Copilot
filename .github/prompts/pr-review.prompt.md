---
name: PR Review
description: Review PharmaChain pull requests for correctness, security and maintainability.
---

# Pull Request Review

## Purpose

Review PharmaChain pull requests for correctness, security and maintainability.

## Review Instructions

1. Inspect the complete Git diff.
2. Understand the purpose of the changes.
3. Check for bugs and regressions.
4. Review authentication and authorization.
5. Check database and data-integrity risks.
6. Review error handling and validation.
7. Check whether tests cover the changes.
8. Identify unnecessary duplication or complexity.

## Review Rules

- Focus on actionable findings.
- Reference the affected file and code.
- Explain why each issue matters.
- Distinguish confirmed defects from suggestions.
- Do not modify files.
- Do not approve changes without sufficient evidence.

## Severity

- Critical: Immediate security or serious data-integrity risk.
- High: Significant functional or security issue.
- Medium: Important defect or missing coverage.
- Low: Minor improvement.

## Final Report

Provide:

- Findings by severity.
- Supporting evidence.
- Recommended improvements.
- Missing tests.
- Overall review recommendation.
