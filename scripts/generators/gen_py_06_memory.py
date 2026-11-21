"""
gen_py_06_memory.py
===================
Generates 01-python/memory-management.md
Contains:
- Basic: PY-BAS-126 to PY-BAS-150 (25 questions)
- Intermediate: PY-INT-126 to PY-INT-150 (25 questions)
- Advanced: PY-ADV-126 to PY-ADV-150 (25 questions)
Total: 75 questions
"""

import os
import sys

# Ensure current dir is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from base import Question, render_file
from mem_basic import basic_data
from mem_inter import inter_data
from mem_adv import adv_data


def build_questions(data_list, difficulty: str):
    qs = []
    for item in data_list:
        qid, title, one_line, detailed, code, desc, internal, rw, follow_ups, mistakes, tip, related, references = item
        qs.append(Question(
            qid=qid,
            title=title,
            difficulty=difficulty,
            topic="Memory Management",
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
    out_file = os.path.join(repo_root, "01-python", "memory-management.md")

    basic_qs = build_questions(basic_data, "Basic")
    inter_qs = build_questions(inter_data, "Intermediate")
    adv_qs = build_questions(adv_data, "Advanced")

    total = len(basic_qs) + len(inter_qs) + len(adv_qs)
    print(f"Generating memory-management.md: {len(basic_qs)} Basic, {len(inter_qs)} Intermediate, {len(adv_qs)} Advanced (Total: {total})")

    content = render_file(
        title="Python Memory Management & Garbage Collection Interview Questions",
        description="Comprehensive technical interview questions covering CPython memory architecture, reference counting, generational cyclic garbage collection, pymalloc arenas/pools/blocks, weakref module, tracemalloc profiling, Copy-On-Write (COW) preservation, PEP 683 immortal objects, free-threaded memory models (PEP 703), and production leak diagnostics.",
        basic_qs=basic_qs,
        inter_qs=inter_qs,
        adv_qs=adv_qs
    )

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote {out_file}")


if __name__ == "__main__":
    main()
