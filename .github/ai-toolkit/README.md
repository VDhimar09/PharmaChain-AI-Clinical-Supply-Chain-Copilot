<!-- @format -->

# PharmaChain AI Toolkit

## Purpose

A reusable collection of GitHub Copilot skills, prompts, instructions and custom agents designed to support consistent AI-assisted software development.

## Where resources live

Copilot-facing resources use the standard repository locations:

- `.github/copilot-instructions.md`: project-wide instructions.
- `.github/instructions/*.instructions.md`: path-specific instructions selected by `applyTo` patterns.
- `.github/agents/*.agent.md`: custom agent definitions.
- `.github/prompts/*.prompt.md`: reusable prompt files.
- `.github/skills/*/SKILL.md`: reusable skills.

The `.github/ai-toolkit/` directory is for maintaining the toolkit itself: documentation, scripts, tests, validation and the generated skills catalog. It does not contain duplicate copies of Copilot-facing resources.

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

- Backend: Python, FastAPI, database and security conventions, applied to `backend/**/*.py`.
- Frontend: React, TypeScript and frontend conventions, applied to `frontend/**/*.{ts,tsx}`.

## How to Use

1. Open the PharmaChain repository in VS Code with GitHub Copilot enabled.
2. Use project instructions automatically as applicable.
3. In Copilot Chat, select a relevant custom agent or invoke a prompt/skill where supported.
4. Provide a specific development task.
5. Review all generated output and changes before accepting them.

## Quality and Validation

Each resource should be tested against a real development scenario.

Record:

- Test scenario
- Expected behaviour
- Actual result
- Issues identified
- Improvements made

Never claim successful validation without evidence.

## Skills catalog

The catalog is generated from each immediate subdirectory of `.github/skills`. Every skill directory must contain a `SKILL.md` file whose first block is YAML front matter delimited by `---`, with non-empty, single-line `name` and `description` fields. Double quotes around values are supported; additional fields are ignored.

```md
---
name: example-skill
description: A concise description of the skill.
---
```

Run `python .github/ai-toolkit/scripts/generate_skills_feed.py` after changing a skill. The generated catalog is `.github/ai-toolkit/skills.json`. Pull requests and pushes validate that the checked-in catalog is current; the scheduled/manual workflow can refresh it.

## Maintenance

- Review resources when project architecture changes.
- Update outdated instructions and examples.
- Document changes in CHANGELOG.md.
- Review contributions before merging.
- Preserve security and data-protection requirements.

## Important

The skills catalog is project-maintained metadata, not itself a native Copilot discovery mechanism. Copilot resource discovery depends on the supported files in the standard locations above.
