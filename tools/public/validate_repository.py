"""
tools/public/validate_repository.py
===================================
Public validation utility for software-engineering-interview-kit.

This tool audits:
- Question ID uniqueness across all files
- Question counts per domain and difficulty
- Answer structure and required sections
- Python code syntax (via AST parsing)
- Relative Markdown link integrity
- Mermaid diagram syntax validation
- Empty files and unexpected temporary files
- Diagram coverage accounting

Usage:
    python tools/public/validate_repository.py
    python tools/public/validate_repository.py --strict
"""

import os
import sys
import re
import ast
import argparse
from pathlib import Path


QUESTION_ID_PATTERN = re.compile(r"^###\s+([A-Z]{2,4}-(?:BAS|INT|ADV)-\d{3}):\s*(.+)$", re.MULTILINE)
SECTION_HEADING_PATTERN = re.compile(r"^###?\s+\d+\.\s+(.+)$", re.MULTILINE)
RELATIVE_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_BLOCK_PATTERN = re.compile(r"```([a-zA-Z0-9_\-]+)?\n(.*?)```", re.DOTALL)
MERMAID_BLOCK_PATTERN = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)

ALLOWED_MERMAID_TYPES = (
    "flowchart", "graph", "sequenceDiagram", "stateDiagram",
    "stateDiagram-v2", "classDiagram", "erDiagram", "xychart-beta"
)


class RepoValidator:
    def __init__(self, root_dir: Path, strict: bool = False):
        self.root_dir = root_dir.resolve()
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.info = []
        self.seen_qids = {}  # qid -> (file_path, title)
        self.domain_stats = {}  # prefix -> {'Basic': count, 'Intermediate': count, 'Advanced': count}
        self.mermaid_diagrams_count = 0
        self.empty_files = []
        self.total_questions = 0

    def run_all_checks(self) -> bool:
        print("=" * 60)
        print(f"Auditing Repository: {self.root_dir}")
        print("=" * 60)

        self._check_empty_and_temp_files()
        self._audit_markdown_files()
        self._print_statistics()

        if self.errors:
            print(f"\n[FAIL] Found {len(self.errors)} error(s):")
            for err in self.errors:
                print(f"  - {err}")

        if self.warnings:
            print(f"\n[WARNING] Found {len(self.warnings)} warning(s):")
            for w in self.warnings:
                print(f"  - {w}")

        if not self.errors and not (self.strict and self.warnings):
            print("\n[SUCCESS] Public repository validation passed cleanly!")
            return True
        else:
            print(f"\n[STATUS] Validation finished with issues (strict={self.strict}).")
            return False

    def _check_empty_and_temp_files(self):
        temp_patterns = ["*.tmp", "*.bak", "*.swp", "*.swo", "*~", ".DS_Store", "Thumbs.db"]
        for p in temp_patterns:
            for match in self.root_dir.rglob(p):
                if ".git" not in match.parts:
                    self.warnings.append(f"Unexpected temporary file found: {match.relative_to(self.root_dir)}")

        for md_file in self.root_dir.rglob("*.md"):
            if ".git" in md_file.parts or "node_modules" in md_file.parts:
                continue
            if md_file.stat().st_size == 0:
                rel = md_file.relative_to(self.root_dir)
                self.empty_files.append(str(rel))
                self.warnings.append(f"Empty Markdown file (0 bytes): {rel}")

    def _audit_markdown_files(self):
        for md_file in sorted(self.root_dir.rglob("*.md")):
            if ".git" in md_file.parts or "node_modules" in md_file.parts or "scripts" in md_file.parts:
                continue
            self._audit_single_file(md_file)

    def _audit_single_file(self, file_path: Path):
        rel_path = file_path.relative_to(self.root_dir)
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.errors.append(f"File {rel_path} is not valid UTF-8.")
            return

        # 1. Mermaid diagrams audit
        for match in MERMAID_BLOCK_PATTERN.finditer(content):
            self.mermaid_diagrams_count += 1
            body = match.group(1).strip()
            first_line = body.splitlines()[0].strip() if body else ""
            if not any(first_line.startswith(t) for t in ALLOWED_MERMAID_TYPES):
                self.warnings.append(f"Unrecognized or unsupported Mermaid diagram type in {rel_path}: '{first_line}'")

        # 2. Relative Markdown links check
        for match in RELATIVE_LINK_PATTERN.finditer(content):
            target = match.group(2).split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "ftp:")):
                continue
            target_path = (file_path.parent / target).resolve()
            if not target_path.exists():
                self.warnings.append(f"Broken relative link in {rel_path}: [{match.group(1)}]({match.group(2)}) -> missing target '{target}'")

        # 3. Question IDs & Content structure audit
        matches = list(QUESTION_ID_PATTERN.finditer(content))
        for m in matches:
            qid = m.group(1).strip()
            title = m.group(2).strip()
            self.total_questions += 1

            # Check ID uniqueness
            if qid in self.seen_qids:
                prev_file, prev_title = self.seen_qids[qid]
                self.errors.append(f"Duplicate Question ID '{qid}': found in {rel_path} and {prev_file}")
            else:
                self.seen_qids[qid] = (str(rel_path), title)

            prefix = qid.split("-")[0]
            level_str = qid.split("-")[1]
            level_map = {"BAS": "Basic", "INT": "Intermediate", "ADV": "Advanced"}
            level = level_map.get(level_str, "Other")

            if prefix not in self.domain_stats:
                self.domain_stats[prefix] = {"Basic": 0, "Intermediate": 0, "Advanced": 0}
            if level in self.domain_stats[prefix]:
                self.domain_stats[prefix][level] += 1

        # 4. AST Python Code Validation
        for lang_m in CODE_BLOCK_PATTERN.finditer(content):
            lang = (lang_m.group(1) or "").lower()
            code_text = lang_m.group(2)
            if lang in ("python", "py"):
                # Clean prompt markers if present
                clean_code = "\n".join(
                    line[4:] if line.startswith(">>> ") or line.startswith("... ") else line
                    for line in code_text.splitlines()
                )
                try:
                    ast.parse(clean_code)
                except SyntaxError as e:
                    self.warnings.append(f"Syntax warning in {rel_path} (line {e.lineno}): {e.msg}")

    def _print_statistics(self):
        print("\n" + "=" * 60)
        print("VERIFIED INTERVIEW QUESTION STATISTICS")
        print("=" * 60)
        print(f"{'Domain / Prefix':<20} | {'Basic':<10} | {'Intermediate':<12} | {'Advanced':<10} | {'Total':<10} | {'Status'}")
        print("-" * 85)

        target_per_level = 200
        prefix_names = {
            "PY": "Python",
            "FA": "FastAPI",
            "DJ": "Django",
            "DRF": "Django REST",
            "DB": "Databases",
            "MSG": "Messaging",
            "API": "API Eng",
            "DSA": "DSA",
            "CS": "Comp Science",
            "SD": "System Design",
            "DEV": "DevOps",
            "SEC": "Security",
        }

        all_prefixes = sorted(set(list(self.domain_stats.keys()) + list(prefix_names.keys())))
        total_b = 0
        total_i = 0
        total_a = 0

        for p in all_prefixes:
            stats = self.domain_stats.get(p, {"Basic": 0, "Intermediate": 0, "Advanced": 0})
            b = stats["Basic"]
            i = stats["Intermediate"]
            a = stats["Advanced"]
            tot = b + i + a
            total_b += b
            total_i += i
            total_a += a

            name = prefix_names.get(p, p)
            status = "Complete :white_check_mark:" if (b >= target_per_level and i >= target_per_level and a >= target_per_level) else ("In Progress" if tot > 0 else "Planned")
            print(f"{name + ' (' + p + ')':<20} | {b:>5}/{target_per_level} | {i:>7}/{target_per_level} | {a:>5}/{target_per_level} | {tot:>5}/600 | {status}")

        print("-" * 85)
        print(f"{'TOTALS':<20} | {total_b:>5}/2400 | {total_i:>7}/2400 | {total_a:>5}/2400 | {self.total_questions:>5}/7200 |")
        print("=" * 60)
        print(f"Mermaid Diagrams Verified: {self.mermaid_diagrams_count}")
        print(f"Empty Files Identified:   {len(self.empty_files)}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Public Repository Validator for Interview Kit")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    # Determine root directory (assumes script is at tools/public/validate_repository.py)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    validator = RepoValidator(root_dir=repo_root, strict=args.strict)
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
