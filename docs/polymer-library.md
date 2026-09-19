# Polymer Library (Phase 3)

The Polymer Library is a scientific data-management interface. It preserves the distinction between polymer identity, supplied structure representations, property definitions, individual property records, and provenance.

## API

`GET /api/v1/polymers` supports `q`, `polymer_class`, `architecture`, `property_key`, `provenance_type`, `sort`, `order`, `limit`, and `offset`. Responses use `items`, `total`, `limit`, and `offset`; `limit` is 1–100.

Use `POST /api/v1/provenance` before linking a record through `POST /api/v1/polymers/{id}/properties`. Property records always retain a property definition, raw value/unit, scientific origin, optional conditions, and linked provenance. `POST /api/v1/polymers/{id}/structures` adds a supplied representation after creation. `PATCH /api/v1/polymers/{id}` updates conservative identity metadata only.

There are no destructive endpoints. Referenced property definitions and provenance remain deletion-protected.

## Frontend

`/polymers` provides library search and pagination. `/polymers/new` creates a polymer and optional unverified structure representation. `/polymers/{id}` separates identity, structures, property records, and provenance, and supplies a compact property-record form.

Phase 3 does not provide chemical validation, structure drawing, similarity/substructure search, unit conversion, AI prediction, or simulation.
