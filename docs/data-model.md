# Scientific Polymer Data Model (Phase 2.1)

## Why Polymer is not SMILES

A `Polymer` identifies material chemistry; `PolymerStructure` stores one supplied repeat-unit or molecular representation. A representation does not fully determine a polymer material or its properties: molecular weight, architecture, composition, morphology, processing, and measurement conditions can matter. The platform stores representations transparently and does not use RDKit or claim chemical syntax validation.

```text
Polymer
   |-- PolymerStructure
   `-- PropertyRecord -- PropertyDefinition
                     `-- Provenance
```

`PropertyRecord` is one value with a unit, optional uncertainty and conditions, required provenance type, and optional traceable `Provenance`. A referenced provenance source cannot be silently removed from a scientific property record. Nor can a referenced property definition be silently removed. These restrictions are enforced by database foreign keys, not only application behavior.

## Units, metadata, and structure claims

Values retain their supplied `value` and `unit`; the platform does not silently convert units. `PropertyDefinition.canonical_unit` records a preferred unit, such as Tg `K`, density `g/cm^3`, band gap `eV`, Young's modulus `GPa`, and dielectric constant `dimensionless`.

Nullable Mn (g/mol), Mw (g/mol), dispersity, and degree of polymerization are MVP identity-level conveniences and have positive-value database checks. They frequently belong to a future `MaterialSample`; polymer chemistry identity and physical material sample remain distinct concepts. `composition_metadata` is transitional JSON only and must not be a future AI-model dependency.

`is_canonical` is supplied metadata only in Phase 2.1. It does not mean the platform chemically validated or canonicalized the structure. Example fixtures consequently set it to `false`. Chemical validation and canonicalization belong to a future Polymer Cheminformatics phase.

## Deletion behavior

For this MVP, database deletion of a `Polymer` cascades to its structures and property records, preventing orphans. This is database integrity behavior, not a user-facing scientific data-retention policy: there is no DELETE API. Future production policy may use archiving or soft deletion rather than destructive deletion.

## Explicitly deferred

Phase 2.1 does not model tacticity, detailed stereochemistry, sequence statistics, blends, additives, fillers, morphology, processing, sample preparation, or detailed protocols. It also adds no RDKit, unit conversion, ML, simulation, agents, RAG, or UI. Future concepts may include `MaterialSample`, `PolymerComposition`, `PolymerComponent`, `ProcessingHistory`, `Measurement`, `SimulationRun`, and `ModelPrediction`.

## Example records

Polystyrene, Polyethylene, Poly(ethylene oxide), Tg, density, and band gap examples are non-inserting fixtures. Structures are not RDKit-validated. Test property values use manual provenance that identifies them as synthetic software fixtures, never experimental reference data.
