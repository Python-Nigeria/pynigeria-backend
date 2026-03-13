# Contributing to PyNigeria Backend

Thank you for your interest in contributing to the official Python Nigeria website backend! We welcome contributions from everyone.

## Table of Contents

- [Contributing to PyNigeria Backend](#contributing-to-pynigeria-backend)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [Getting Started](#getting-started)
  - [Development Setup](#development-setup)
  - [How to Contribute](#how-to-contribute)
  - [Branch Naming](#branch-naming)
  - [Commit Messages](#commit-messages)
  - [Pull Request Process](#pull-request-process)
  - [Reporting Bugs](#reporting-bugs)
  - [Requesting Features](#requesting-features)

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pynigeria-backend.git
   cd pynigeria-backend
   ```
3. **Add the upstream remote:**
   ```bash
   git remote add upstream https://github.com/Python-Nigeria/pynigeria-backend.git
   ```
4. **Keep your fork in sync:**
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

---

## Development Setup

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Install dependencies** (uv will create a virtual environment automatically):
   ```bash
   uv sync
   ```

3. **Copy the example env file and fill in your values:**
   ```bash
   cp .env.example .env
   ```

4. **Apply migrations:**
   ```bash
   uv run python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   uv run python manage.py runserver
   ```

6. **Run tests to confirm everything works:**
   ```bash
   uv run python manage.py test
   ```

---

## How to Contribute

- Look for issues tagged [`good first issue`](https://github.com/Python-Nigeria/pynigeria-backend/labels/good%20first%20issue) if you're new.
- Comment on an issue before starting work to avoid duplication.
- For significant changes, open an issue first to discuss the approach.

---

## Branch Naming

Use the following conventions:

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<short-description>` | `feature/job-search-filter` |
| Bug fix | `fix/<short-description>` | `fix/auth-token-expiry` |
| Chore/tooling | `chore/<short-description>` | `chore/update-dependencies` |
| Documentation | `docs/<short-description>` | `docs/api-endpoints` |

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `ci`

**Examples:**
```
feat(jobs): add salary range filter to job listing API
fix(auth): resolve JWT token refresh race condition
docs(contributing): add branch naming conventions
```

---

## Pull Request Process

1. Ensure your branch is up to date with `main` before opening a PR.
2. Make sure all tests pass:
   ```bash
   uv run python manage.py test
   ```
3. Ensure your code is formatted with Black:
   ```bash
   uv run black .
   ```
4. Fill out the pull request template completely.
5. Link the relevant issue using `Closes #<issue-number>` in your PR description.
6. Request a review from a maintainer.
7. Address all review comments before merging.

PRs that do not pass CI checks will not be merged.

---

## Reporting Bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml) issue template. Include:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version, OS, and relevant environment details


---

## Requesting Features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml) issue template. Describe:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered
