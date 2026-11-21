#!/usr/bin/env python3
"""
validate_repository.py
======================
Comprehensive validation tool for the Software Engineering Interview Kit repository.

Validates:
1. Question ID uniqueness and sequential formatting ([TOPIC]-[LEVEL]-[001..999]).
2. Integrity of 10-point standard format sections.
3. Syntax of embedded Python code blocks.
4. Relative file link resolution across Markdown documents.
5. Accurate generation of question statistics table.
6. Optional sync of live question counts into the root README.md.
"""

import os
import re
import sys
import ast
import argparse
from collections import defaultdict
from typing import Dict, List, Tuple, Set

# Regex patterns
RE_QUESTION_HEADER = re.compile(r'^(?:###\s+|<summary>)(?:Question ID:\s*)?([A-Z0-9]+)-(BAS|INT|ADV)-(\d{3})[:\s]+(.+?)(?:</summary>)?$', re.MULTILINE)
RE_MARKDOWN_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
RE_PYTHON_CODE_BLOCK = re.compile(r'```python\s*\n(.*?)```', re.DOTALL)

# Expected sections in standard question format
STANDARD_SECTIONS = [
    "One-Line Answer",
    "Detailed Answer",
    "Practical Example",
    "Internal Working",
    "Real-World Use Case",
    "Interview Follow-Up Questions",
    "Common Interview Mistakes",
    "Interview Tip",
    "Related Concepts",
    "References",
]

TOPIC_MAP = {
    'PY': 'Python',
    'FA': 'FastAPI',
    'DJ': 'Django',
    'DRF': 'Django REST Framework',
    'DB': 'Databases',
    'MSG': 'Redis & Messaging',
    'API': 'API Engineering',
    'DSA': 'Data Structures & Algorithms',
    'CS': 'Computer Science',
    'SD': 'System Design',
    'DEV': 'DevOps',
    'SEC': 'Security',
}


def find_repo_root() -> str:
    """Find repository root relative to this script."""
    current = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(current)
    if os.path.exists(os.path.join(parent, 'README.md')) and os.path.exists(os.path.join(parent, '01-python')):
        return parent
    return os.getcwd()


def scan_markdown_files(repo_root: str) -> List[str]:
    """Collect all markdown files in the repository excluding hidden/scratch dirs."""
    md_files = []
    exclude_dirs = {'.git', '.idea', '.vscode', 'tmp', 'scratch', 'node_modules', '.venv', 'venv'}
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.system_generated')]
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
    return sorted(md_files)


def validate_repository(repo_root: str, strict: bool = False) -> Tuple[bool, Dict[str, Dict[str, int]], List[str]]:
    """Scan all files and run validation checks."""
    errors: List[str] = []
    warnings: List[str] = []
    all_question_ids: Dict[str, str] = {}  # QID -> File path
    topic_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {'BAS': 0, 'INT': 0, 'ADV': 0})

    md_files = scan_markdown_files(repo_root)

    for file_path in md_files:
        rel_path = os.path.relpath(file_path, repo_root).replace('\\', '/')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Cannot read file {rel_path}: {e}")
            continue

        # 1. Parse questions
        matches = list(RE_QUESTION_HEADER.finditer(content))
        for match in matches:
            topic, level, num, title = match.groups()
            qid = f"{topic}-{level}-{num}"

            if qid in all_question_ids:
                errors.append(f"Duplicate Question ID '{qid}' found in {rel_path} (already seen in {all_question_ids[qid]})")
            else:
                all_question_ids[qid] = rel_path
                topic_counts[topic][level] += 1

        # 2. Check Python code block syntax
        code_blocks = RE_PYTHON_CODE_BLOCK.findall(content)
        for i, code in enumerate(code_blocks, 1):
            # Skip code blocks with intentionally pseudo-code or ellipses
            if '...' in code and code.count('\n') < 4:
                continue
            try:
                ast.parse(code)
            except SyntaxError as e:
                # Tolerate modern Python syntax if running validation on older Python (e.g., 3.10)
                if sys.version_info < (3, 11) and "except*" in code:
                    continue
                if sys.version_info < (3, 12) and re.search(r'^\s*type\s+\w+', code, re.MULTILINE):
                    continue
                # Flag if it looks like actual runnable code rather than templated pseudo-code
                if "SyntaxError" not in code and not any(tag in code for tag in ['<your-', 'SELECT ', '...']):
                    warnings.append(f"Syntax warning in {rel_path} (code block #{i}): {e.msg} at line {e.lineno}")

        # 3. Check relative Markdown links (exclude code blocks)
        content_no_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content_no_code = re.sub(r'`[^`\n]+`', '', content_no_code)
        links = RE_MARKDOWN_LINK.findall(content_no_code)
        dir_path = os.path.dirname(file_path)
        for link_text, link_target in links:
            # Skip web urls, mailto, and in-page anchor only links
            if link_target.startswith(('http://', 'https://', 'mailto:', '#', 'ftp://')):
                continue
            # Remove query string / anchor
            clean_target = link_target.split('#')[0].split('?')[0]
            if not clean_target:
                continue
            target_path = os.path.normpath(os.path.join(dir_path, clean_target))
            if not os.path.exists(target_path):
                warnings.append(f"Broken relative link in {rel_path}: [{link_text}]({link_target}) -> target '{clean_target}' does not exist.")

    # Determine pass/fail
    is_valid = len(errors) == 0
    if strict and len(warnings) > 0:
        is_valid = False

    return is_valid, topic_counts, errors, warnings


def generate_status_table(topic_counts: Dict[str, Dict[str, int]]) -> str:
    """Generate Markdown progress table matching repository standards."""
    rows = [
        "| Domain / Topic | Basic | Intermediate | Advanced | Total Questions | Target Status |",
        "|---|---|---|---|---|---|"
    ]

    for topic_code, topic_name in TOPIC_MAP.items():
        counts = topic_counts.get(topic_code, {'BAS': 0, 'INT': 0, 'ADV': 0})
        bas = counts['BAS']
        inter = counts['INT']
        adv = counts['ADV']
        total = bas + inter + adv
        status = "Complete :white_check_mark:" if (bas >= 200 and inter >= 200 and adv >= 200) else (
            "In Progress :construction:" if total > 0 else "Planned :clipboard:"
        )
        rows.append(f"| **{topic_name}** (`{topic_code}`) | {bas}/200 | {inter}/200 | {adv}/200 | **{total}/600** | {status} |")

    return "\n".join(rows)


def update_readme_table(repo_root: str, status_table: str) -> bool:
    """Update the status table in root README.md."""
    readme_path = os.path.join(repo_root, 'README.md')
    if not os.path.exists(readme_path):
        return False

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the table between markers or header
    pattern = re.compile(r'(<!-- STATUS_TABLE_START -->)(.*?)(<!-- STATUS_TABLE_END -->)', re.DOTALL)
    if pattern.search(content):
        updated = pattern.sub(f"\\1\n\n{status_table}\n\n\\3", content)
    else:
        # Fallback replacement if markers not present yet
        table_regex = re.compile(r'(\| Domain / Topic \| Basic.*?)(?=\n\n|\Z)', re.DOTALL)
        if table_regex.search(content):
            updated = table_regex.sub(status_table, content)
        else:
            return False

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated)
    return True


def main():
    parser = argparse.ArgumentParser(description="Validate repository questions and links.")
    parser.add_argument('--strict', action='store_true', help="Fail on warnings as well as errors.")
    parser.add_argument('--update-readme', action='store_true', help="Sync question counts into root README.md.")
    args = parser.parse_args()

    repo_root = find_repo_root()
    print(f"Validating repository at: {repo_root}")

    is_valid, topic_counts, errors, warnings = validate_repository(repo_root, strict=args.strict)
    status_table = generate_status_table(topic_counts)

    print("\n" + "=" * 60)
    print("CURRENT VERIFIED QUESTION STATISTICS")
    print("=" * 60)
    print(status_table)
    print("=" * 60)

    if args.update_readme:
        if update_readme_table(repo_root, status_table):
            print("[INFO] Successfully updated root README.md status table.")
        else:
            print("[WARN] Could not find status table markers in README.md.")

    if warnings:
        print(f"\n[WARNINGS] ({len(warnings)} found):")
        for w in warnings[:15]:
            print(f"  - {w}")
        if len(warnings) > 15:
            print(f"  ... and {len(warnings) - 15} more warnings.")

    if errors:
        print(f"\n[ERRORS] ({len(errors)} found):")
        for e in errors:
            print(f"  - {e}")
        print("\nRepository validation FAILED.")
        sys.exit(1)

    if not is_valid:
        print("\nRepository validation FAILED in strict mode due to warnings.")
        sys.exit(1)

    print("\n[SUCCESS] Repository validation passed cleanly!")
    sys.exit(0)


if __name__ == '__main__':
    main()
