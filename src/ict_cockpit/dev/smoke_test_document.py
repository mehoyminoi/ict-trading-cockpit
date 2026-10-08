from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


STATUSES = ("PASS", "FAIL", "QUESTION", "NOT TESTED")
_STATUS_RE = re.compile(
    r"^(?P<indent>\s*)- \[(?P<status>PASS|FAIL|QUESTION|NOT TESTED)\] (?P<text>.*)$"
)


@dataclass
class SmokeTestItem:
    index: int
    section: str
    text: str
    status: str
    comments: list[str]
    line_index: int
    comment_end_index: int
    indent: str = ""


class SmokeTestDocument:
    """Round-trip editor for status-bearing manual smoke-test Markdown items.

    Only lines explicitly marked with one of the supported status tokens are
    treated as validation items. Other Markdown remains untouched.
    """

    def __init__(self, lines: list[str], items: list[SmokeTestItem]) -> None:
        self.lines = lines
        self.items = items

    @classmethod
    def from_text(cls, text: str) -> "SmokeTestDocument":
        lines = text.splitlines()
        items: list[SmokeTestItem] = []
        section = ""
        index = 0

        while index < len(lines):
            line = lines[index]
            if line.startswith("#"):
                section = line.lstrip("#").strip()

            match = _STATUS_RE.match(line)
            if match is None:
                index += 1
                continue

            indent = match.group("indent")
            comment_prefix = indent + "  - "
            comments: list[str] = []
            comment_index = index + 1
            while (
                comment_index < len(lines)
                and lines[comment_index].startswith(comment_prefix)
            ):
                comments.append(lines[comment_index][len(comment_prefix) :])
                comment_index += 1

            items.append(
                SmokeTestItem(
                    index=len(items),
                    section=section,
                    text=match.group("text"),
                    status=match.group("status"),
                    comments=comments,
                    line_index=index,
                    comment_end_index=comment_index,
                    indent=indent,
                )
            )
            index = comment_index

        return cls(lines, items)

    @classmethod
    def load(cls, path: str | Path) -> "SmokeTestDocument":
        return cls.from_text(Path(path).read_text(encoding="utf-8"))

    def summary(self) -> dict[str, int]:
        return {
            status: sum(item.status == status for item in self.items)
            for status in STATUSES
        }

    @property
    def accepted(self) -> bool:
        return bool(self.items) and all(
            item.status == "PASS" for item in self.items
        )

    def update_item(
        self,
        item_index: int,
        *,
        status: str,
        comments: list[str] | None = None,
    ) -> None:
        if status not in STATUSES:
            raise ValueError(f"unsupported smoke-test status: {status}")
        item = self.items[item_index]
        item.status = status
        item.comments = [
            comment.strip()
            for comment in list(comments or [])
            if comment.strip()
        ]

    def to_text(self) -> str:
        item_by_line = {item.line_index: item for item in self.items}
        rendered: list[str] = []
        line_index = 0

        while line_index < len(self.lines):
            item = item_by_line.get(line_index)
            if item is None:
                rendered.append(self.lines[line_index])
                line_index += 1
                continue

            rendered.append(
                f"{item.indent}- [{item.status}] {item.text}"
            )
            comment_prefix = item.indent + "  - "
            rendered.extend(
                comment_prefix + comment for comment in item.comments
            )
            line_index = item.comment_end_index

        return "\n".join(rendered) + "\n"

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_text(), encoding="utf-8")
