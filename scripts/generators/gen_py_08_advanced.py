"""
gen_py_08_advanced.py
=====================
Generates 01-python/advanced-python.md
Contains:
- Basic: PY-BAS-176 to PY-BAS-200 (25 questions)
- Intermediate: PY-INT-176 to PY-INT-200 (25 questions)
- Advanced: PY-ADV-176 to PY-ADV-200 (25 questions)
Total: 75 questions
"""

import os
import sys

# Ensure current dir is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from base import Question, render_file
from adv_py_basic import basic_data
from adv_py_inter import inter_data
from adv_py_adv import adv_data


def build_questions(data_list, difficulty: str):
    qs = []
    for item in data_list:
        qid, title, one_line, detailed, code, desc, internal, rw, follow_ups, mistakes, tip, related, references = item
        qs.append(Question(
            qid=qid,
            title=title,
            difficulty=difficulty,
            topic="Advanced Python",
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
    out_file = os.path.join(repo_root, "01-python", "advanced-python.md")

    basic_qs = build_questions(basic_data, "Basic")
    inter_qs = build_questions(inter_data, "Intermediate")
    adv_qs = build_questions(adv_data, "Advanced")

    total = len(basic_qs) + len(inter_qs) + len(adv_qs)
    print(f"Generating advanced-python.md: {len(basic_qs)} Basic, {len(inter_qs)} Intermediate, {len(adv_qs)} Advanced (Total: {total})")

    content = render_file(
        title="Advanced Python Programming & Metaprogramming Interview Questions",
        description="Comprehensive technical interview questions covering metaclasses, class creation lifecycle (__prepare__, __new__, __init__), __init_subclass__, descriptors, static and structural typing (typing.Protocol, TypeVar, ParamSpec), structural pattern matching (PEP 634), contextlib advanced patterns, custom import hooks (sys.meta_path), C-extension architecture (PEP 489), PyO3 Rust extensions, and enterprise software design.",
        basic_qs=basic_qs,
        inter_qs=inter_qs,
        adv_qs=adv_qs
    )

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote {out_file}")


if __name__ == "__main__":
    main()
