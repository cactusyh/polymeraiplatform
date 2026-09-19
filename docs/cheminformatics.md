# Phase 4 Cheminformatics

## Scope and stored structure

A PolymerStructure preserves the submitted **raw representation** exactly. Processing stores a separate normalized representation and never overwrites provenance input. is_canonical is source metadata supplied by the data provider; it does not assert that this platform canonicalized the raw value.

Supported representation types are conventional smiles, psmiles, and repeat_unit_smiles. Other types are preserved but receive unsupported. PSMILES is interpreted as an RDKit graph under the current supported checks. Wildcard (*) dummy atoms represent attachment points; their count is persisted. Exactly two is common for a linear repeat unit, while another count is partially_valid, not automatically chemically invalid.

Validation statuses are not_validated, valid, partially_valid, invalid, and unsupported. An unprocessed record is not_validated with no validation timestamp. Every processing attempt, including invalid and unsupported input, records validated_at; processing also records the RDKit and normalization versions where meaningful.

## Normalization and descriptors

Normalization is deterministic canonical RDKit SMILES for a parsable structure. It is a derived representation, not a claim to complete polymer identity. Derived descriptor keys are heavy_atom_count, heteroatom_count, ring_count, aromatic_ring_count, rotatable_bond_count, and fraction_csp3. They are graph descriptors and are deliberately not named Mn or Mw.

## Attachment-aware fingerprint and similarity

The on-demand fingerprint is Morgan, radius 2, 2048 bits, with wildcards_retained. Wildcard attachment environments therefore influence the fingerprint; they are not stripped and no hydrogen-capped fingerprint is introduced in Phase 4.1. Tanimoto is the intersection-over-union comparison of these bit vectors. The API and interface call the output **repeat-unit structural similarity**, not polymer similarity, confidence, or probability. No bit vector is returned to a client.

This is not a complete polymer fingerprint. It does not encode Mn, Mw, dispersity, DP, full tacticity unless represented, copolymer sequence statistics, morphology, crystallinity, processing, formulation, crosslink-network topology, experimental conditions, or any material-property outcome.

## Backfill

Run python -m backend.app.chemistry.backfill explicitly to process existing structures. It is safe to rerun, preserves raw input, updates all derived metadata consistently, reports valid/partially-valid/invalid/unsupported counts, and rolls back its transaction on failure. It is never run at application startup.
