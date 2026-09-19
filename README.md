# Polymer AI Platform

## Current status

**Phase 3 — Polymer Scientific Data Management.** The platform provides a FastAPI/SQLAlchemy polymer library with PostgreSQL-oriented Alembic migrations and a Next.js scientific data-management UI. It distinguishes polymer identity, structure representations, property definitions, property records, and provenance.

## Run

```bash
conda env create -f environment.yml
conda activate polymer-ai
cp .env.example .env
docker compose up -d postgres
alembic upgrade head
uvicorn backend.app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000/polymers` to search the Polymer Library, add polymer identities and supplied structure representations, inspect scientific records/provenance, and add property records.

## Library API

`GET /api/v1/polymers` supports paginated `q`, `polymer_class`, `architecture`, `property_key`, and `provenance_type` filters plus controlled sorting. The API also provides provenance creation/listing, property-definition listing, structure attachment, Polymer PATCH, and property-record listing.

See [docs/polymer-library.md](docs/polymer-library.md) and [docs/data-model.md](docs/data-model.md).

## Validate

```bash
pytest
DATABASE_URL=sqlite+pysqlite:////tmp/polymer-ai.sqlite alembic upgrade head
DATABASE_URL=sqlite+pysqlite:////tmp/polymer-ai.sqlite alembic check
cd frontend && npm run build
```

Chemical validation, structure similarity, unit conversion, AI prediction, and simulation are intentionally not available yet. There are no destructive API endpoints.

## Next milestone

Phase 4 — Polymer Cheminformatics Foundation.
