# Polymer AI Platform

Polymer AI Platform is an evolving AI-native research foundation for polymer materials. It will incrementally bring together polymer data, scientific models, uncertainty-aware predictions, and reproducible research workflows.

## Current status

**Phase 1 — platform foundation.** The repository currently provides a minimal FastAPI backend, a Next.js frontend, environment-driven configuration, PostgreSQL development infrastructure, and backend smoke tests. It does not yet include polymer data models, property prediction, AI agents, RAG, or simulation capabilities.

## Architecture

```text
Browser
   │
   ▼
Next.js Frontend
   │
   ▼
FastAPI Backend
   │
   ▼
PostgreSQL
```

Scientific ML, agent, retrieval, and simulation layers will be introduced incrementally in later phases.

## Requirements

- Git
- Conda (or Miniforge)
- Node.js and npm
- Docker with Docker Compose for the optional local PostgreSQL service

## Python environment

Create the isolated project environment. Do not reuse unrelated research environments.

```bash
conda env create -f environment.yml
conda activate polymer-ai
```

## Configuration

```bash
cp .env.example .env
```

`DATABASE_URL` is reserved for future database connectivity. The Phase 1 API starts without PostgreSQL, so the database is optional while developing the health endpoints.

## Database

When Docker is installed and running:

```bash
docker compose up -d postgres
```

The Compose credentials are intentionally development-only. Do not use them outside local development.

## Run the backend

From the repository root:

```bash
uvicorn backend.app.main:app --reload
```

Endpoints:

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/api/v1/info`

## Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The page checks `http://127.0.0.1:8000/health` by default. To use another backend URL, set `NEXT_PUBLIC_API_BASE_URL` before starting Next.js.

## Test

From the repository root, with `polymer-ai` active:

```bash
pytest
```

## Next milestone

Phase 2 will introduce a minimal scientifically sound polymer data model with first-class metadata and provenance.
