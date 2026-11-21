"""
gen_fa_07_middleware.py
=======================
Generates 02-fastapi/middleware-and-exception-handling.md
Contains:
- Basic: FA-BAS-151 to FA-BAS-175 (25 questions)
- Intermediate: FA-INT-151 to FA-INT-175 (25 questions)
- Advanced: FA-ADV-151 to FA-ADV-175 (25 questions)
Total: 75 questions
"""

import os
import sys

# Ensure current dir is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from base import Question, render_file
from fa_mid_basic import basic_data
from fa_mid_inter import inter_data
from fa_mid_adv import adv_data


def build_questions(data_list, difficulty: str):
    qs = []
    for item in data_list:
        qid, title, one_line, detailed, code, desc, internal, rw, follow_ups, mistakes, tip, related, references = item
        qs.append(Question(
            qid=qid,
            title=title,
            difficulty=difficulty,
            topic="FastAPI Middleware & Exception Handling",
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
    out_file = os.path.join(repo_root, "02-fastapi", "middleware-and-exception-handling.md")

    basic_qs = build_questions(basic_data, "Basic")
    inter_qs = build_questions(inter_data, "Intermediate")
    adv_qs = build_questions(adv_data, "Advanced")

    total = len(basic_qs) + len(inter_qs) + len(adv_qs)
    print(f"Generating middleware-and-exception-handling.md: {len(basic_qs)} Basic, {len(inter_qs)} Intermediate, {len(adv_qs)} Advanced (Total: {total})")

    content = render_file(
        title="FastAPI Middleware & Exception Handling Interview Questions",
        description="Comprehensive technical interview questions covering ASGI middleware architecture, BaseHTTPMiddleware, pure ASGI 3-callable implementation, CORS, security headers, rate limiting, exception handlers, RFC 7807 problem details, and error boundaries.",
        basic_qs=basic_qs,
        inter_qs=inter_qs,
        adv_qs=adv_qs
    )

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote {out_file}")


if __name__ == "__main__":
    main()
