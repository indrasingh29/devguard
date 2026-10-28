# DevGuard AI — Production & Free-Tier Deployment Guide

This guide covers deploying DevGuard AI locally with Docker Compose and to production using verified free-tier platforms.

---

## 1. Local Deployment with Docker Compose

### Prerequisites
- Docker & Docker Compose (`docker version >= 24.0`)
- A GitHub Personal Access Token (classic: `public_repo` scope)

### Quick Start
1. Clone the repository and copy configuration:
   ```bash
   git clone https://github.com/your-username/devguard.git
   cd devguard
   cp .env.example .env
   ```

2. Start all services (PostgreSQL, Backend, Frontend):
   ```bash
   docker compose up --build -d
   ```

3. Access the services:
   - **Frontend Dashboard**: `http://localhost`
   - **Backend API**: `http://localhost:8000/api/v1/healthz`
   - **Interactive API Documentation**: `http://localhost:8000/docs`

4. Verify migration status:
   ```bash
   docker compose exec backend alembic current
   ```

---

## 2. Free-Tier Cloud Deployment Architecture

| Component | Recommended Free Provider | Limitations & Mitigations |
| :--- | :--- | :--- |
| **Frontend** | **Vercel** / **Cloudflare Pages** | Unlimited static bandwidth. Free SSL and custom domain. |
| **Backend API** | **Render** / **Railway** / **Fly.io** | Render Free Web Service (512MB RAM, sleeps after 15m inactivity). Handled gracefully with healthcheck probes. |
| **Database** | **Neon** / **Supabase** (PostgreSQL) | Neon offers a generous serverless PostgreSQL free tier (0.5GB storage, branching). Perfect for DevGuard schema. |

### Step 2.1: Provisioning Free PostgreSQL (Neon)
1. Sign up at [neon.tech](https://neon.tech).
2. Create a project named `devguard-prod`.
3. Copy the connection string:
   ```
   postgresql://devguard_owner:[PASSWORD]@[HOST].neon.tech/devguard?sslmode=require
   ```

### Step 2.2: Deploying Backend (Render)
1. Sign up at [render.com](https://render.com) and create a new **Web Service**.
2. Connect your GitHub repository and select the `backend` root.
3. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string.
   - `ENVIRONMENT`: `production`
   - `GITHUB_TOKEN`: Your GitHub token.
   - `CORS_ORIGINS`: Your Vercel frontend URL.

### Step 2.3: Deploying Frontend (Vercel)
1. Sign up at [vercel.com](https://vercel.com) and import the repository.
2. Set **Root Directory** to `frontend`.
3. Set **Framework Preset** to `Vite`.
4. Add Environment Variable:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://devguard-api.onrender.com`).
5. Deploy!

---

## 3. Database Migrations & Rollback Safety

- **Run pending migrations**:
  ```bash
  alembic upgrade head
  ```
- **Inspect current revision**:
  ```bash
  alembic current
  ```
- **Safe Rollback**:
  ```bash
  alembic downgrade -1
  ```
