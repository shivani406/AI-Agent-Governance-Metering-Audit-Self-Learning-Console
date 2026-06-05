# Contributing to AI-Agent-Governance-Metering-Audit-Self-Learning-Console

Thank you for your interest in contributing to AI-Agent-Governance-Metering-Audit-Self-Learning-Console! We welcome all contributions, including bug reports, feature requests, documentation updates, and code changes.

## 🚀 How to Get Started

## 1. Reporting Bugs & Feature Requests
Before creating a new issue, please check the existing issues to see if your topic has already been discussed. If not, open a new issue and include:
* A clear, descriptive title.
* Steps to reproduce the issue (if a bug).
* Expected vs. actual behavior.


## 📥 2. Install Poetry (Dependency Manager)
This project uses **Poetry 2.0+** to manage runtime dependencies, isolation groups, and package artifacts. If you do not have Poetry installed, execute the official installation vector for your OS:

### Linux, macOS, and WSL
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows (PowerShell)
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python3 -
```

### Verify Installation
Restart your terminal shell and run the following command to confirm Poetry is active:
```bash
poetry --version
```

---

## 📂 3. Local Environment Setup
Follow these commands in sequence to clone the project and install its ecosystem layers:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/shivani406/AI-Agent-Governance-Metering-Audit-Self-Learning-Console
   cd agent-governance-console
   ```

2. **Install Dependencies:**
   Run the installation routine from the root folder to provision a virtual environment and install requirements:
   ```bash
   poetry install
   ```

3. **Activate the Virtual Environment:**
   Spawn a shell nested inside your newly isolated environment workspace:
   ```bash
   poetry shell
   ```

---

## 🛠️ 4. Pre-Submission Validation Checklist
To maintain code quality, our CI/CD pipeline runs testing and linting sweeps on every branch. **You must execute all three commands below locally** before committing. If any check fails, your PR will be blocked.

### Rule 1: Run the Automated Test Suite
Verify your modifications do not introduce regressions:
```bash
poetry run pytest -v
```

### Rule 2: Scan for Issues and Code Bugs
Analyze the codebase structure using **Ruff** for syntax errors or non-standard naming:
```bash
poetry run ruff check .
```
*(Tip: Use `poetry run ruff check . --fix` to resolve minor issues automatically).*

### Rule 3: Format Your Files Dynamically
Enforce consistent formatting (indentation, quotations, and line length):
```bash
poetry run ruff format .
```

---

## 🚀 5. Submitting Your Changes
1. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your_feature_name
   ```
2. **Implement Changes:**
   * Use `snake_case` for variables.
   * Keep code free of unnecessary comments.
   * Ensure proper indentation.
3. **Validate:** Complete the **Pre-Submission Validation Checklist** above.
4. **Push & PR:** Commit your changes cleanly, push your branch to GitHub, and open a **Pull Request**. Detail your architectural additions, the problem solved, and confirm that all local tests passed.


## 🛠️ Your Contribution Workflow

Please follow this git workflow to submit your changes:

1. **Create a branch:** Create a descriptive feature branch from the main branch.
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes:** Write your code, update tests, and ensure local formatting checks pass.
3. **Commit your changes:** Write clear, concise commit messages.
4. **Push your branch:** Push your new branch back up to your GitHub fork.
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request (PR):** Navigate to the original repository on GitHub and click "Compare & pull request".

## 📋 Pull Request Guidelines

Before your PR can be merged, it must meet these criteria:
* The code must follow the project's style guidelines.
* Existing and new test suites must pass successfully.
* Your PR description must clearly explain *what* changes were made and *why*.
* Link your PR to any relevant issues by adding "Closes #123" to the description.

