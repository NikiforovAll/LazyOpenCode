"""Parser for Skill customizations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
    SkillFile,
    SkillMetadata,
)
from lazyopencode.services.parsers import (
    ICustomizationParser,
    parse_frontmatter,
    read_file_safe,
)

if TYPE_CHECKING:
    from lazyopencode.services.gitignore_filter import GitignoreFilter


def _read_skill_files(
    directory: Path,
    exclude: set[str] | None = None,
    gitignore_filter: GitignoreFilter | None = None,
) -> list[SkillFile]:
    """Recursively read all files in a skill directory."""
    if exclude is None:
        exclude = set()

    files: list[SkillFile] = []
    try:
        # Sort entries: directories first, then alphabetically
        entries = sorted(
            directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
        )
    except OSError:
        return files

    for entry in entries:
        # Skip excluded files and hidden files
        if entry.name in exclude or entry.name.startswith("."):
            continue

        if entry.is_dir():
            # Skip gitignored directories
            if gitignore_filter and (
                gitignore_filter.should_skip_dir(entry.name)
                or gitignore_filter.is_dir_ignored(entry)
            ):
                continue

            children = _read_skill_files(entry, exclude, gitignore_filter)
            files.append(
                SkillFile(
                    name=entry.name,
                    path=entry,
                    is_directory=True,
                    children=children,
                )
            )
        elif entry.is_file():
            try:
                content = entry.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                content = None
            files.append(
                SkillFile(
                    name=entry.name,
                    path=entry,
                    content=content,
                )
            )

    return files


class SkillParser(ICustomizationParser):
    """Parses skill/*/SKILL.md files."""

    def __init__(
        self,
        skills_dir: Path | None = None,
        gitignore_filter: GitignoreFilter | None = None,
    ) -> None:
        """Initialize with optional skills directory and gitignore filter."""
        self._skills_dir = skills_dir
        self._filter = gitignore_filter

    def can_parse(self, path: Path) -> bool:
        """Check if path is a SKILL.md file in a skill directory."""
        return (
            path.is_file()
            and path.name == "SKILL.md"
            and path.parent.parent.name == "skill"
        )

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse skill file and detect directory contents."""
        skill_dir = path.parent
        content, error = read_file_safe(path)

        if error:
            return Customization(
                name=skill_dir.name,
                type=CustomizationType.SKILL,
                level=level,
                path=path,
                error=error,
            )

        frontmatter, _ = parse_frontmatter(content or "")

        # Extract name from frontmatter or fallback to directory name
        name = frontmatter.get("name", skill_dir.name)
        description = frontmatter.get("description")

        # Recursively read all files in the skill directory
        skill_files = _read_skill_files(
            skill_dir, exclude={"SKILL.md"}, gitignore_filter=self._filter
        )

        # Build metadata with file tree
        metadata = SkillMetadata(files=skill_files)

        return Customization(
            name=name,
            type=CustomizationType.SKILL,
            level=level,
            path=path,
            description=description or f"Skill: {skill_dir.name}",
            metadata=metadata.__dict__,
            content=content,
            error=error,
        )
