# Contributing to DevGuard AI

Thank you for contributing to DevGuard AI!

## Development Workflow

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (or local SQLite development fallback)
- Docker & Docker Compose (optional for local multi-container testing)

### 2. Setting Up Backend
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Setting Up Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Code Quality & Pre-commit Checks
Before submitting a pull request, run all linters and tests:
```bash
# Backend linting and tests
cd backend
ruff check app tests
bandit -r app -x app/core/security.py
pytest -v

# Frontend type checking and tests
cd ../frontend
npm run build
npm test

# Run the synthetic benchmark
cd ..
python evals/run_eval.py
```

### 5. Adding New Static Analysis Rules
To introduce a new rule:
1. Navigate to `backend/app/engine/rules/`.
2. Choose the appropriate category module (`security.py`, `secrets.py`, `bugs.py`, `quality.py`).
3. Define the rule specification with a unique ID (e.g. `VULN-007`), regex/AST matcher, severity, category, message, and actionable suggested remediation.
4. Add a test case in `backend/tests/test_static_analyzer.py` and benchmark entry in `evals/run_eval.py`.
