"""Parser for Claude Code skill customizations."""

from pathlib import Path
from typing import TYPE_CHECKING

from lazyopencode.models.customization import (
    ConfigLevel,
    ConfigSource,
    Customization,
    CustomizationType,
    SkillFile,
    SkillMetadata,
)
from lazyopencode.services.parsers import parse_frontmatter

if TYPE_CHECKING:
    from lazyopencode.services.gitignore_filter import GitignoreFilter


def _read_skill_files(
    directory: Path,
    exclude: set[str] | None = None,
    gitignore_filter: "GitignoreFilter | None" = None,
) -> list[SkillFile]:
    """Recursively read all files in a skill directory."""
    if exclude is None:
        exclude = set()

    files: list[SkillFile] = []
    try:
        entries = sorted(
            directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
        )
    except OSError:
        return files

    for entry in entries:
        if entry.name in exclude or entry.name.startswith("."):
            continue

        if entry.is_dir():
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


class SkillParser:
    """Parser for skill directories.

    File pattern: skills/*/SKILL.md
    """

    def __init__(
        self,
        skills_dir: Path,
        gitignore_filter: "GitignoreFilter | None" = None,
    ) -> None:
        """Initialize with the skills directory path."""
        self.skills_dir = skills_dir
        self._filter = gitignore_filter

    def can_parse(self, path: Path) -> bool:
        """Check if path is a SKILL.md file in a skill subdirectory."""
        return path.name == "SKILL.md" and path.parent.parent == self.skills_dir

    def parse(self, path: Path, level: ConfigLevel, source_level: str) -> Customization:
        """Parse a skill SKILL.md file and detect directory contents."""
        skill_dir = path.parent

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            return Customization(
                name=skill_dir.name,
                type=CustomizationType.SKILL,
                level=level,
                path=path,
                error=f"Failed to read file: {e}",
                source=ConfigSource.CLAUDE_CODE,
                source_level=source_level,
            )

        frontmatter, _ = parse_frontmatter(content)

        name = frontmatter.get("name", skill_dir.name)
        description = frontmatter.get("description")

        skill_files = _read_skill_files(
            skill_dir, exclude={"SKILL.md"}, gitignore_filter=self._filter
        )

        metadata = SkillMetadata(files=skill_files)

        return Customization(
            name=name,
            type=CustomizationType.SKILL,
            level=level,
            path=path,
            description=description,
            content=content,
            metadata=metadata.__dict__,
            source=ConfigSource.CLAUDE_CODE,
            source_level=source_level,
        )
