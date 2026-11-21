"""
gen_fa_02_routing.py
====================
Generates 02-fastapi/routing-and-dependencies.md
Contains:
- Basic: FA-BAS-026 to FA-BAS-050 (25 questions)
- Intermediate: FA-INT-026 to FA-INT-050 (25 questions)
- Advanced: FA-ADV-026 to FA-ADV-050 (25 questions)
Total: 75 questions
"""

import os
import sys

# Ensure current dir is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from base import Question, render_file
from fa_routing_basic import basic_data
from fa_routing_inter import inter_data
from fa_routing_adv import adv_data


def build_questions(data_list, difficulty: str):
    qs = []
    for item in data_list:
        qid, title, one_line, detailed, code, desc, internal, rw, follow_ups, mistakes, tip, related, references = item
        qs.append(Question(
            qid=qid,
            title=title,
            difficulty=difficulty,
            topic="FastAPI Routing & Dependency Injection",
            one_line=one_line,
            detailed=detailed,
            example_code=code,
            example_desc=desc,
            internal_working=internal,
            real_world=rw,
            follow_ups=follow_ups,
            mistakes=mistakes,
            tip=tip,
            related=related,
            references=references
        ))
    return qs


def main():
    repo_root = os.path.dirname(os.path.dirname(curr_dir))
    out_file = os.path.join(repo_root, "02-fastapi", "routing-and-dependencies.md")

    basic_qs = build_questions(basic_data, "Basic")
    inter_qs = build_questions(inter_data, "Intermediate")
    adv_qs = build_questions(adv_data, "Advanced")

    total = len(basic_qs) + len(inter_qs) + len(adv_qs)
    print(f"Generating routing-and-dependencies.md: {len(basic_qs)} Basic, {len(inter_qs)} Intermediate, {len(adv_qs)} Advanced (Total: {total})")

    content = render_file(
        title="FastAPI Routing & Dependency Injection Interview Questions",
        description="Comprehensive technical interview questions covering APIRouter modularization, path/query/header extraction, Dependency Injection (DI) architecture, DAG resolution, yield dependencies, security scopes, and high-performance routing internals.",
        basic_qs=basic_qs,
        inter_qs=inter_qs,
        adv_qs=adv_qs
    )

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote {out_file}")


if __name__ == "__main__":
    main()
