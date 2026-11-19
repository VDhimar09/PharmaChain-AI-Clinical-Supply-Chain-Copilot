<!-- @format -->

# PharmaChain AI Toolkit

## Purpose

A reusable collection of GitHub Copilot skills, prompts, instructions and agents designed to support consistent AI-assisted software development.

## Toolkit Components

### Skills

- Python Testing: Guidance for writing reliable FastAPI and pytest tests.
- API Development: Guidance for developing and validating backend APIs.

### Prompts

- API Test Generator: Creates structured API test plans.
- Bug Investigation: Investigates issues and identifies root causes.
- PR Review: Reviews proposed code changes.

### Custom Agents

- Code Reviewer: Reviews code quality, security and maintainability.
- Test Engineer: Identifies test gaps and recommends test scenarios.
- Architecture Reviewer: Reviews architecture and design decisions.

### Instructions

- Backend: Python, FastAPI, database and security conventions.
- Frontend: React, TypeScript and frontend development conventions.

## How to Use

1. Open the PharmaChain repository in VS Code.
2. Open GitHub Copilot Chat.
3. Select the relevant skill, prompt or custom agent.
4. Provide a specific development task.
5. Review the output before accepting changes.

## Quality and Validation

Each resource should be tested against a real development scenario.

Record:

- Test scenario
- Expected behaviour
- Actual result
- Issues identified
- Improvements made

Never claim successful validation without evidence.

## Maintenance

- Review resources when project architecture changes.
- Update outdated instructions and examples.
- Document changes in CHANGELOG.md.
- Review contributions before merging.
- Preserve security and data-protection requirements.

### Skills feed metadata

The weekly skills-feed automation reads every immediate subdirectory of
`.github/ai-toolkit/skills`. Each directory must contain a `SKILL.md` file.
Its first block must be YAML front matter delimited by `---` and contain
non-empty, single-line `name` and `description` fields. Double quotes around a
value are supported; additional fields are ignored.

```md
---
name: example-skill
description: A concise description of the skill.
---
```

Run `python .github/ai-toolkit/scripts/generate_skills_feed.py` after changing
a skill and commit the resulting `skills.json` update. Pull requests and pushes
also verify that the checked-in catalog is current.

## Important

This library documents reusable resources. Copilot discovery and execution depend on the supported integration files in the relevant project.
