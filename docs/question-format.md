# Question Format Specification

To guarantee uniform quality, high instructional value, and interview readiness across the entire repository, all questions must follow the 10-point standard format.

---

## The 10-Point Standard Template

Every question follows this format:

```markdown
### [QUESTION_ID]: [Question Title]

**Difficulty:** [Basic | Intermediate | Advanced]  
**Topic:** [Subtopic Name]

#### 1. One-Line Answer
A concise, punchy 1-2 sentence core definition or summary that can be immediately verbalized in an interview phone screen.

#### 2. Detailed Answer
A technically rigorous explanation that details:
- What the concept is.
- Why the language or framework designed it this way.
- How it operates in practice.
- Architectural trade-offs and best practices.

#### 3. Practical Example
A clean, runnable code snippet demonstrating the concept in action. Avoid pseudo-code unless illustrating theoretical algorithms.
```python
# Valid, tested, self-contained snippet
```
*Brief explanation of what the snippet demonstrates.*

#### 4. Internal Working
Under-the-hood execution mechanics (CPython data structures, bytecode, memory allocations, OS system calls, database storage pages) where applicable.

#### 5. Real-World Use Case
Realistic production scenario illustrating where and why a backend software engineer uses this concept in live applications.

#### 6. Interview Follow-Up Questions
2 to 5 targeted follow-up questions commonly asked by interviewers after the candidate delivers the primary answer:
- *Follow-up 1?*
- *Follow-up 2?*
- *Follow-up 3?*

#### 7. Common Interview Mistakes
Common candidate blunders, misconceptions, or outdated practices (e.g., using mutable default arguments, confusing threads with processes, assuming Redis is purely in-memory with zero durability options).

#### 8. Interview Tip
Strategic tactical advice on how to present the response clearly, manage time, and demonstrate seniority.

#### 9. Related Concepts
Cross-references linking to relevant subtopics or questions within this repository.

#### 10. References
Authoritative references pointing to official documentation (docs.python.org, postgresql.org, redis.io, etc.).
```

---

## When to Adapt Sections

Certain theoretical, architectural, or conceptual questions may not require every technical field (e.g., pure behavioral or high-level architecture questions may not have a 10-line Python code snippet). However, for all core engineering questions, contributors must provide the complete 10 points.

---

## Quality Rules

1. **Originality**: Answers must be written with original technical clarity, not copied verbatim from tutorials or AI-generated hallucinations without technical verification.
2. **Precision**: Explain the *why* behind technical decisions, not merely the *what*.
3. **Runnable Code**: Python code snippets must execute without errors under Python 3.10+.
