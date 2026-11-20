# Contributing to Software Engineering Interview Kit

Thank you for your interest in contributing to the **Software Engineering Interview Kit**! This open-source repository aims to be the most comprehensive, technically accurate, and community-driven resource for Python-focused software engineering, backend systems, and DevOps interviews.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Repository Workflow](#repository-workflow)
- [Question Formatting Standards](#question-formatting-standards)
- [Question ID Conventions](#question-id-conventions)
- [Duplicate Policy](#duplicate-policy)
- [Code Quality & Testing](#code-quality--testing)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Validation Script](#validation-script)

---

## Code of Conduct

All contributors and participants must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to repository maintainers.

---

## How Can I Contribute?

You can contribute in several ways:
1. **Adding New Questions**: Add missing interview questions matching our 10-point standard format.
2. **Improving Existing Explanations**: Deepen explanations, add internal runtime mechanics, or improve diagrammatic clarity.
3. **Adding Production Scenarios**: Contribute real-world engineering troubleshooting experiences and case studies.
4. **Fixing Code Examples**: Verify, optimize, or fix Python, SQL, Docker, or Nginx configurations.
5. **Fixing Typos or Broken Links**: Maintain documentation cleanliness and link integrity.

---

## Repository Workflow

1. **Fork the Repository**: Click "Fork" on GitHub to create your personal copy.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/<your-username>/software-engineering-interview-kit.git
   cd software-engineering-interview-kit
   ```
3. **Create a branch**: Name your branch descriptively.
   ```bash
   git checkout -b feat/python-advanced-internals
   # or
   git checkout -b fix/fastapi-auth-typo
   ```
4. **Make changes**: Follow our formatting and quality guidelines.
5. **Run the local validation tool**:
   ```bash
   py scripts/validate_repository.py
   # or
   python scripts/validate_repository.py
   ```
6. **Commit with semantic messages**:
   ```bash
   git commit -m "feat(python): add PY-ADV-015 GIL multi-core execution details"
   ```
7. **Push and create a Pull Request**: Submit your PR targeting `main`.

---

## Question Formatting Standards

Every question added must adhere to our standardized structure. Consolidated markdown files must use consistent headers or `<details>` blocks.

### Standard Structure

```markdown
### [QUESTION_ID]: [Concise, Clear Question Title]

**Difficulty:** [Basic | Intermediate | Advanced]  
**Topic:** [Specific Subtopic Name]

#### 1. One-Line Answer
A concise, 1-2 sentence core definition or summary that can be stated immediately in an interview.

#### 2. Detailed Answer
A thorough, technically accurate explanation covering:
- What the concept is.
- Why it is designed this way.
- How it operates.
- Trade-offs and best practices.

#### 3. Practical Example
A runnable, minimal Python / SQL / Bash code snippet illustrating the concept.
```python
# Clear, idiomatic code snippet
```
*Explanation of the code snippet above.*

#### 4. Internal Working
Deep dive into runtime internals (CPython bytecode, GIL, memory layouts, OS system calls, database execution engines) where applicable.

#### 5. Real-World Use Case
Concrete production scenario where a backend engineer encounters or leverages this concept.

#### 6. Interview Follow-Up Questions
- *Follow-up 1?*
- *Follow-up 2?*
- *Follow-up 3?*

#### 7. Common Interview Mistakes
- Misconception 1: ...
- Misconception 2: ...

#### 8. Interview Tip
Strategic advice on how to structure the verbal response during a live interview.

#### 9. Related Concepts
- [Linked Topic 1](../path/to/file.md)
- [Linked Topic 2](../path/to/file.md)

#### 10. References
- [Official Documentation Title](https://docs.python.org/3/...)
```

---

## Question ID Conventions

Question IDs follow a strict format: `[TOPIC_CODE]-[LEVEL]-[NUMBER]`

| Topic | Code | Example Basic | Example Intermediate | Example Advanced |
|---|---|---|---|---|
| Python | `PY` | `PY-BAS-001` | `PY-INT-001` | `PY-ADV-001` |
| FastAPI | `FA` | `FA-BAS-001` | `FA-INT-001` | `FA-ADV-001` |
| Django | `DJ` | `DJ-BAS-001` | `DJ-INT-001` | `DJ-ADV-001` |
| Django REST Framework | `DRF` | `DRF-BAS-001` | `DRF-INT-001` | `DRF-ADV-001` |
| Databases & SQL | `DB` | `DB-BAS-001` | `DB-INT-001` | `DB-ADV-001` |
| Redis & Messaging | `MSG` | `MSG-BAS-001` | `MSG-INT-001` | `MSG-ADV-001` |
| API Engineering | `API` | `API-BAS-001` | `API-INT-001` | `API-ADV-001` |
| Data Structures & Algorithms | `DSA` | `DSA-BAS-001` | `DSA-INT-001` | `DSA-ADV-001` |
| Computer Science | `CS` | `CS-BAS-001` | `CS-INT-001` | `CS-ADV-001` |
| System Design | `SD` | `SD-BAS-001` | `SD-INT-001` | `SD-ADV-001` |
| DevOps & Cloud | `DEV` | `DEV-BAS-001` | `DEV-INT-001` | `DEV-ADV-001` |
| Security | `SEC` | `SEC-BAS-001` | `SEC-INT-001` | `SEC-ADV-001` |

---

## Duplicate Policy

- **Zero Tolerance for Rephrased Duplicates**: Check existing files before creating a question. If a question already asks "What is GIL?", do not add "Explain Global Interpreter Lock" as a separate ID.
- **Deepening Existing Questions**: If an existing question lacks depth, submit an improvement to that question rather than creating a second one.
- **Run the Validator**: Our validator checks for duplicate titles and duplicated Question IDs.

---

## Code Quality & Testing

1. All Python code snippets must be syntactically valid for Python 3.10+.
2. Code must follow PEP 8 style conventions and use descriptive variable names.
3. Code must not contain undefined variables or mock-ups that fail standard parsing.
4. Avoid external dependencies unless the question topic specifically requires it (e.g. `fastapi`, `django`, `redis`, `pydantic`).

---

## Pull Request Guidelines

Before submitting your PR:
- [ ] Run `python scripts/validate_repository.py` and confirm all tests pass.
- [ ] Ensure all questions follow the 10-point standard format.
- [ ] Ensure Question IDs are unique and sequential.
- [ ] Ensure Markdown links resolve to real paths.
- [ ] Complete the Pull Request template checklist.
