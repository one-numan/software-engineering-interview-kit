# Contributor Guide: Software Engineering Interview Kit

Thank you for your interest in contributing to the **Software Engineering Interview Kit**! This repository is an open-source, community-driven resource built to provide world-class interview preparation for developers worldwide.

---

## 🛠️ How to Contribute

We welcome contributions of all levels:
- Adding new interview questions.
- Improving existing answers with deeper architectural explanations.
- Adding edge-case code examples and debugging scenarios.
- Reporting errata, broken links, or outdated documentation references.
- Translating or organizing learning roadmaps.

---

## 📋 The 10-Point Question Standard

Every question submitted to this repository **must** strictly adhere to the 10-point standard format:

```markdown
### TOPIC-DIFF-XXX: Title of the Question

**Difficulty:** Basic | Intermediate | Advanced
**Topic:** Exact Topic Name

#### 1. One-Line Answer
Concise, spoken summary suitable for a quick interview response.

#### 2. Detailed Answer
Deep, technically rigorous explanation covering how, why, and trade-offs.

#### 3. Practical Example
```python
# Syntactically valid, runnable code block
```
Clear explanation of how the code executes.

#### 4. Internal Working
Under-the-hood runtime mechanics (e.g. CPython C structures, memory allocators, ASGI dispatch, kernel page caches).

#### 5. Real-World Use Case
Concrete production architecture scenario where this concept applies.

#### 6. Interview Follow-Up Questions
2–3 questions an interviewer might ask to probe deeper.

#### 7. Common Mistakes
2–3 common anti-patterns or misunderstandings candidates make.

#### 8. Interview Tip
Actionable advice on how to structure your response during an interview.

#### 9. Related Concepts
Relative Markdown links to related files (e.g. `[Python OOP](01-python/oop.md)`).

#### 10. References
Links to official documentation (Python docs, FastAPI docs, PEPs, RFCs).
```

---

## 🚀 Git & Contribution Workflow

### 1. Fork and Clone
```bash
git clone https://github.com/<your-username>/software-engineering-interview-kit.git
cd software-engineering-interview-kit
```

### 2. Create a Feature Branch
```bash
git checkout -b feat/add-fastapi-dependency-questions
```

### 3. Make Your Changes
Add or edit questions in the consolidated Markdown files under the appropriate topic directory.

### 4. Run the Validation Suite
Before opening a pull request, always run the repository validation tool:
```bash
python tools/public/validate_repository.py
```
For complete rules on formatting, typography, and architectural diagrams, refer to [Documentation Standards](docs/DOCUMENTATION_STANDARDS.md).
The test suite checks:
- Question header regex formatting and uniqueness.
- Syntax validity of all Python code blocks using `ast.parse()`.
- Integrity of all relative Markdown links.
- Correct difficulty labels (Basic, Intermediate, Advanced).

### 5. Submit Your Pull Request
Push your branch to your fork and submit a PR against `main`. Make sure to complete the PR checklist!

---

## 🏆 Contributor Recognition Program

We celebrate our contributors:
- **All-Contributors Wall:** Every merged PR is added to our contributors list in `README.md`.
- **Monthly Spotlight:** Outstanding technical contributions are highlighted across our community channels and release notes.
- **Good First Issues:** Browse issues labeled [`good first issue`](https://github.com/one-numan/software-engineering-interview-kit/labels/good%20first%20issue) to get started!
