# DevGuard AI — REST API Reference (`/api/v1`)

DevGuard exposes a fully versioned RESTful API with automated OpenAPI specifications accessible at `/docs` (Swagger UI) and `/redoc`.

---

## 1. System & Health

### `GET /api/v1/healthz`
Liveness probe checking if the API worker process is responsive.
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "service": "DevGuard AI",
    "version": "1.0.0"
  }
  ```

### `GET /api/v1/ready`
Readiness probe verifying active database connectivity.
- **Response**: `200 OK`
  ```json
  {
    "status": "ready",
    "database": "connected",
    "service": "DevGuard AI"
  }
  ```

### `GET /api/v1/settings/status`
Public system configuration and integration readiness (no secrets exposed).

---

## 2. Repositories

### `POST /api/v1/repositories/connect`
Connect a GitHub repository for monitoring and audits.
- **Request Body**:
  ```json
  {
    "repo_input": "octocat/Hello-World"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": 1,
    "owner": "octocat",
    "name": "Hello-World",
    "full_name": "octocat/Hello-World",
    "default_branch": "master",
    "is_private": false,
    "html_url": "https://github.com/octocat/Hello-World",
    "created_at": "2026-10-28T22:30:00Z",
    "updated_at": "2026-10-28T22:30:00Z",
    "open_prs_count": 0,
    "total_reviews_count": 0
  }
  ```

### `GET /api/v1/repositories`
List all connected repositories.

---

## 3. Pull Requests & Reviews

### `POST /api/v1/pull-requests/fetch-diff`
Retrieve and parse changed files, hunks, and line mappings without running a job.
- **Request Body**:
  ```json
  {
    "repo_full_name": "octocat/Hello-World",
    "pull_number": 12
  }
  ```

### `POST /api/v1/reviews/start`
Trigger code review pipeline on a pull request.
- **Request Body**:
  ```json
  {
    "repo_full_name": "octocat/Hello-World",
    "pull_number": 12,
    "mode": "deterministic"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "id": 4,
    "pull_request_id": 1,
    "commit_sha": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d",
    "status": "COMPLETED",
    "mode": "deterministic",
    "total_files_analyzed": 1,
    "total_findings": 0,
    "summary": "Analyzed 1 changed files (+1/-0 lines). Identified 0 findings in 210ms using deterministic engine.",
    "execution_time_ms": 210,
    "severity_counts": {
      "critical": 0,
      "high": 0,
      "medium": 0,
      "low": 0,
      "info": 0
    },
    "findings": []
  }
  ```

### `GET /api/v1/reviews/{job_id}`
Get full findings, severity counts, and status for a specific review job.

### `GET /api/v1/reviews`
List review history with pagination and search.
- **Query Parameters**:
  - `repo_full_name`: string (optional filter)
  - `status`: string (`COMPLETED`, `PROCESSING`, `QUEUED`, `FAILED`)
  - `limit`: int (default: 50)
  - `offset`: int (default: 0)

---

## 4. Findings & Quality Audit

### `GET /api/v1/findings/{finding_id}`
Get single finding details, evidence, and remediation advice.

### `POST /api/v1/findings/{finding_id}/feedback`
Submit user feedback on a finding.
- **Request Body**:
  ```json
  {
    "finding_id": 101,
    "feedback_type": "helpful",
    "comment": "Accurate SQL injection detection."
  }
  ```
- **Response**: `201 Created`

---

## 5. Webhooks

### `POST /api/v1/webhooks/github`
Process GitHub pull request events with HMAC-SHA256 signature verification.
- **Headers**:
  - `X-Hub-Signature-256`: `sha256=...`
  - `X-GitHub-Event`: `pull_request`
  - `X-GitHub-Delivery`: `guid`
