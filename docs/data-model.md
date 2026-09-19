# Scientific Polymer Data Model (Phase 2)

## Why Polymer is not SMILES

A `Polymer` identifies the material chemistry, while `PolymerStructure` stores one supplied representation of its repeat-unit or molecular structure. A single representation does not fully determine a polymer material or its properties: molecular weight, architecture, composition, morphology, processing, and measurement conditions can all matter. Phase 2 stores structures transparently; it does not use RDKit or claim chemical syntax validation.

The relationship is deliberately small and explicit:

```text
Polymer
   |-- PolymerStructure
   `-- PropertyRecord -- PropertyDefinition
                     `-- Provenance
```

`PropertyRecord` is one particular value in a particular unit, with optional uncertainty and conditions. Its required `provenance_type` distinguishes experiment, simulation, prediction, literature, and unknown. Its optional `Provenance` supplies traceability. Thus numerical values are not presented as scientifically interchangeable.

## Units and MVP metadata

Every record retains its supplied `value` and `unit`; Phase 2 never silently converts units. `PropertyDefinition.canonical_unit` documents a preferred unit, e.g. Tg `K`, density `g/cm^3`, band gap `eV`, Young's modulus `GPa`, and dielectric constant `dimensionless`.

`Polymer` temporarily permits nullable Mn (g/mol), Mw (g/mol), dispersity (dimensionless), and degree of polymerization (dimensionless). This is an MVP convenience only. These quantities are often sample-specific, so future code must treat `Polymer` chemistry identity and `MaterialSample` physical material as distinct. A future path is `Polymer -> MaterialSample -> PropertyMeasurement`, without rewriting this core model.

`composition_metadata` is optional JSON for limited transitional copolymer information. It may hold component labels and fractions, but future AI models must not depend on it. A normalized composition model can replace it later.

## Explicitly not modeled yet

Phase 2 does not fully model tacticity; stereochemistry beyond supplied structure representations; copolymer sequence statistics; blends; additives; fillers; formulations; crosslink topology; morphology; processing history; sample preparation; or detailed experimental protocols. It also adds no RDKit, descriptors, ML, simulation, agents, or RAG.

Likely future concepts are `MaterialSample`, `PolymerComposition`, `PolymerComponent`, `ProcessingHistory`, `Measurement`, `SimulationRun`, and `ModelPrediction`. Prediction-specific details such as model name/version and dataset version can temporarily live in `Provenance.metadata`; a model registry is intentionally deferred.

## Example records

The repository includes non-inserting example definitions for Polystyrene, Polyethylene, and Poly(ethylene oxide), and for Tg, density, and band gap. Their structure strings are examples only and are explicitly not RDKit-validated. Any test property values use manual provenance with notes identifying them as synthetic software fixtures, not experimental reference data.
