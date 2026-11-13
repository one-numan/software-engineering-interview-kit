"""
base.py
=======
Common data structures and rendering utilities for question bank generators.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Question:
    qid: str
    title: str
    difficulty: str  # Basic, Intermediate, Advanced
    topic: str
    one_line: str
    detailed: str
    example_code: Optional[str] = None
    example_desc: Optional[str] = None
    internal_working: Optional[str] = None
    real_world: Optional[str] = None
    follow_ups: Optional[List[str]] = None
    mistakes: Optional[List[str]] = None
    tip: Optional[str] = None
    related: Optional[List[str]] = None
    references: Optional[List[str]] = None

    def render(self) -> str:
        lines = []
        lines.append(f"### {self.qid}: {self.title}\n")
        lines.append(f"**Difficulty:** {self.difficulty} | **Topic:** {self.topic}\n")
        lines.append("#### 1. One-Line Answer")
        lines.append(f"{self.one_line}\n")
        lines.append("#### 2. Detailed Answer")
        lines.append(f"{self.detailed}\n")

        # Collapsible technical deep-dive
        lines.append("<details>")
        lines.append(f"<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>\n")

        if self.example_code:
            lines.append("#### 3. Practical Example")
            lines.append(f"```python\n{self.example_code.strip()}\n```")
            if self.example_desc:
                lines.append(f"*{self.example_desc}*\n")
            else:
                lines.append("")

        if self.internal_working:
            lines.append("#### 4. Internal Working")
            lines.append(f"{self.internal_working}\n")

        if self.real_world:
            lines.append("#### 5. Real-World Use Case")
            lines.append(f"{self.real_world}\n")

        if self.follow_ups:
            lines.append("#### 6. Interview Follow-Up Questions")
            for q in self.follow_ups:
                lines.append(f"- {q}")
            lines.append("")

        if self.mistakes:
            lines.append("#### 7. Common Interview Mistakes")
            for m in self.mistakes:
                lines.append(f"- {m}")
            lines.append("")

        if self.tip:
            lines.append("#### 8. Interview Tip")
            lines.append(f"{self.tip}\n")

        if self.related:
            lines.append("#### 9. Related Concepts")
            for r in self.related:
                lines.append(f"- {r}")
            lines.append("")

        if self.references:
            lines.append("#### 10. References")
            for ref in self.references:
                lines.append(f"- {ref}")
            lines.append("")

        lines.append("</details>\n")
        lines.append("---\n")
        return "\n".join(lines)


def render_file(title: str, description: str, basic_qs: List[Question], inter_qs: List[Question], adv_qs: List[Question]) -> str:
    lines = []
    lines.append(f"# {title}\n")
    lines.append(f"{description}\n")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append(f"- [Basic Level ({len(basic_qs)} Questions)](#basic-level)")
    for q in basic_qs:
        anchor = f"{q.qid.lower()}-{q.title.lower().replace(' ', '-').replace('?', '').replace('(', '').replace(')', '').replace(':', '').replace('/', '').replace(',', '').replace('`', '')}"
        lines.append(f"  - [{q.qid}: {q.title}](#{q.qid.lower()}-{q.title.lower().replace(' ', '-').replace('?', '').replace('(', '').replace(')', '').replace(':', '').replace('/', '').replace(',', '').replace('`', '')})")

    lines.append(f"- [Intermediate Level ({len(inter_qs)} Questions)](#intermediate-level)")
    for q in inter_qs:
        lines.append(f"  - [{q.qid}: {q.title}](#{q.qid.lower()}-{q.title.lower().replace(' ', '-').replace('?', '').replace('(', '').replace(')', '').replace(':', '').replace('/', '').replace(',', '').replace('`', '')})")

    lines.append(f"- [Advanced Level ({len(adv_qs)} Questions)](#advanced-level)")
    for q in adv_qs:
        lines.append(f"  - [{q.qid}: {q.title}](#{q.qid.lower()}-{q.title.lower().replace(' ', '-').replace('?', '').replace('(', '').replace(')', '').replace(':', '').replace('/', '').replace(',', '').replace('`', '')})")

    lines.append("\n---\n")

    # Basic section
    lines.append("## Basic Level\n")
    for q in basic_qs:
        lines.append(q.render())

    # Intermediate section
    lines.append("## Intermediate Level\n")
    for q in inter_qs:
        lines.append(q.render())

    # Advanced section
    lines.append("## Advanced Level\n")
    for q in adv_qs:
        lines.append(q.render())

    return "\n".join(lines)
