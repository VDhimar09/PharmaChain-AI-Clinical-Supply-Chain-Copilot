"""Generate a deterministic JSON catalog for repository Copilot skills."""

from __future__ import annotations

import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIRECTORY = REPOSITORY_ROOT / ".github" / "skills"
OUTPUT_PATH = REPOSITORY_ROOT / ".github" / "ai-toolkit" / "skills.json"
REQUIRED_FIELDS = ("name", "description")


def read_front_matter(skill_path: Path) -> dict[str, str]:
    """Read the simple name/description front matter used by project skills."""
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{skill_path} must start with YAML front matter.")

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break

        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip('"')
    else:
        raise ValueError(f"{skill_path} has unterminated YAML front matter.")

    missing_fields = [field for field in REQUIRED_FIELDS if not metadata.get(field)]
    if missing_fields:
        raise ValueError(
            f"{skill_path} is missing required front matter: "
            + ", ".join(missing_fields)
        )

    return metadata


def build_feed(
    skills_directory: Path = SKILLS_DIRECTORY,
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, object]:
    """Build a sorted catalog from each skill's canonical SKILL.md file."""
    skills = []
    for skill_directory in sorted(skills_directory.iterdir()):
        if not skill_directory.is_dir():
            continue

        skill_path = skill_directory / "SKILL.md"
        if not skill_path.is_file():
            raise FileNotFoundError(f"{skill_directory} is missing SKILL.md.")

        metadata = read_front_matter(skill_path)
        skills.append(
            {
                "name": metadata["name"],
                "description": metadata["description"],
                "path": skill_path.relative_to(repository_root).as_posix(),
            }
        )

    return {
        "schema_version": 1,
        "skills": sorted(skills, key=lambda skill: str(skill["name"])),
    }


def main() -> None:
    """Write the catalog in a stable form suitable for source control."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(build_feed(), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
