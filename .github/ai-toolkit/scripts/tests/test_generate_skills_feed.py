"""Tests for the repository Copilot skills catalog generator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).parents[1] / "generate_skills_feed.py"
SPEC = importlib.util.spec_from_file_location("generate_skills_feed", SCRIPT_PATH)
assert SPEC and SPEC.loader
feed_generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(feed_generator)


def write_skill(directory: Path, front_matter: str) -> None:
    directory.mkdir()
    (directory / "SKILL.md").write_text(front_matter, encoding="utf-8")


def test_build_feed_sorts_skills_and_uses_canonical_paths(tmp_path: Path) -> None:
    skills_directory = tmp_path / ".github" / "ai-toolkit" / "skills"
    skills_directory.mkdir(parents=True)
    write_skill(
        skills_directory / "zebra",
        "---\nname: zebra\ndescription: Last skill\n---\n",
    )
    write_skill(
        skills_directory / "alpha",
        "---\nname: alpha\ndescription: First skill\n---\n",
    )

    feed = feed_generator.build_feed(skills_directory, tmp_path)

    assert feed == {
        "schema_version": 1,
        "skills": [
            {
                "name": "alpha",
                "description": "First skill",
                "path": ".github/ai-toolkit/skills/alpha/SKILL.md",
            },
            {
                "name": "zebra",
                "description": "Last skill",
                "path": ".github/ai-toolkit/skills/zebra/SKILL.md",
            },
        ],
    }


def test_build_feed_fails_when_a_skill_directory_lacks_skill_file(tmp_path: Path) -> None:
    skills_directory = tmp_path / "skills"
    skills_directory.mkdir()
    (skills_directory / "missing-skill").mkdir()

    with pytest.raises(FileNotFoundError, match="missing-skill.*SKILL.md"):
        feed_generator.build_feed(skills_directory, tmp_path)


@pytest.mark.parametrize(
    "front_matter, message",
    [
        ("name: no-delimiter\n", "must start with YAML front matter"),
        ("---\nname: unfinished\n", "unterminated YAML front matter"),
        ("---\nname: incomplete\n---\n", "missing required front matter: description"),
    ],
)
def test_read_front_matter_rejects_invalid_required_metadata(
    tmp_path: Path, front_matter: str, message: str
) -> None:
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(front_matter, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        feed_generator.read_front_matter(skill_path)
