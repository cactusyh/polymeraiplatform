# Polymer AI Platform

Polymer AI Platform is an evolving AI-native research foundation for polymer materials. It incrementally brings together polymer data, scientific models, uncertainty-aware predictions, and reproducible research workflows.

## Current status

**Phase 2 — scientific polymer data model.** The platform now separates polymer identity, supplied structure representations, property definitions, individual property records, and provenance. It has no RDKit, property-prediction, simulation, agent, RAG, or search functionality yet.

## Architecture

```text
Browser -> Next.js Frontend -> FastAPI Backend -> PostgreSQL
                                      |
                                      `-> SQLAlchemy + Alembic
```

See [docs/data-model.md](docs/data-model.md) for the scientific model, its scope, units, and future evolution.

## Requirements

- Git
- Conda (or Miniforge)
- Node.js and npm
- Docker with Docker Compose for the optional local PostgreSQL service

## Python environment

```bash
conda env create -f environment.yml
conda activate polymer-ai
```

## Configuration and database

```bash
cp .env.example .env
docker compose up -d postgres
alembic upgrade head
```

`DATABASE_URL` controls the database connection. The Compose credentials are intentionally development-only; do not use them outside local development. Schema creation is managed through Alembic, not application startup.

## Run the backend

```bash
uvicorn backend.app.main:app --reload
```

Endpoints:

- `GET /health`
- `GET /api/v1/info`
- `POST /api/v1/polymers`
- `GET /api/v1/polymers/{id}`
- `POST /api/v1/property-definitions`
- `GET /api/v1/property-definitions/{id}`
- `POST /api/v1/polymers/{id}/properties`

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The page checks `http://127.0.0.1:8000/health` by default. Set `NEXT_PUBLIC_API_BASE_URL` to use another backend URL.

## Test

```bash
conda run -n polymer-ai pytest
cd frontend && npm run build
```

The test suite uses temporary SQLite databases for portable ORM and API validation. Production is PostgreSQL-oriented; run the migration against PostgreSQL in an environment where it is available.

## Next milestone

Phase 3 — Polymer CRUD, Search, and Scientific Data Management UI.
