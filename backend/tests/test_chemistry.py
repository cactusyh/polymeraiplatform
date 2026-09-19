"""Phase 4.1 chemistry service, API, persistence, and backfill coverage."""
from sqlalchemy.exc import IntegrityError

from backend.app.chemistry.backfill import apply_result
from backend.app.chemistry.service import FINGERPRINT_CONFIG, fingerprint, process, similarity
from backend.app.models import Polymer, PolymerStructure


def test_validation_statuses_timestamps_and_wildcards():
    assert process("smiles", "CCO").status == "valid"
    invalid = process("smiles", "not smiles")
    assert invalid.status == "invalid" and invalid.validated_at is not None
    valid = process("psmiles", "[*]CC[*]")
    assert valid.status == "valid" and valid.connection_point_count == 2
    assert process("psmiles", "[*]CC").status == "partially_valid"
    unsupported = process("other", "kept raw")
    assert unsupported.status == "unsupported" and unsupported.validated_at is not None


def test_normalization_descriptors_and_fingerprint_are_deterministic():
    raw = "C(C)O"
    first, second = process("smiles", raw), process("smiles", raw)
    assert raw == "C(C)O"
    assert first.normalized_representation == second.normalized_representation
    assert first.derived_properties == second.derived_properties
    assert "heavy_atom_count" in first.derived_properties
    assert "Mn" not in first.derived_properties and "Mw" not in first.derived_properties
    assert fingerprint(first.normalized_representation) == fingerprint(second.normalized_representation)
    assert similarity(first.normalized_representation, second.normalized_representation) == 1.0
    assert similarity(first.normalized_representation, process("smiles", "CCC").normalized_representation) < 1.0
    assert FINGERPRINT_CONFIG == {"algorithm":"Morgan","radius":2,"n_bits":2048,"attachment_handling":"wildcards_retained"}


def test_chemistry_endpoints_and_similarity_exclusions(client):
    validation = client.post("/api/v1/chemistry/validate", json={"representation_type":"psmiles","representation":"[*]CC[*]"})
    assert validation.status_code == 200
    assert validation.json()["fingerprint_config"]["attachment_handling"] == "wildcards_retained"
    assert client.post("/api/v1/chemistry/validate", json={"representation_type":"smiles"}).status_code == 422
    assert client.post("/api/v1/chemistry/similarity-search", json={"representation_type":"smiles","representation":"bad input"}).status_code == 422
    good = client.post("/api/v1/polymers", json={"name":"Search good","structures":[{"representation_type":"psmiles","representation":"[*]CC[*]"}]}).json()
    bad = client.post("/api/v1/polymers", json={"name":"Search bad","structures":[{"representation_type":"other","representation":"raw"}]}).json()
    response = client.post("/api/v1/chemistry/similarity-search", json={"representation_type":"psmiles","representation":"[*]CC[*]","minimum_similarity":0,"limit":10})
    assert response.status_code == 200
    ids = [item["polymer_id"] for item in response.json()["items"]]
    assert good["id"] in ids and bad["id"] not in ids


def test_persistence_constraints_detail_and_repeatable_backfill(client, db_session):
    created = client.post("/api/v1/polymers", json={"name":"Persisted chemistry","structures":[{"representation_type":"smiles","representation":"CCO"}]}).json()
    structure = created["structures"][0]
    assert structure["validation_status"] == "valid" and structure["normalized_representation"]
    assert client.get("/api/v1/polymers/" + created["id"]).json()["structures"][0]["rdkit_version"]
    polymer = Polymer(name="Unprocessed", canonical_name="unprocessed")
    structure = PolymerStructure(representation_type="smiles", representation="CCO")
    polymer.structures.append(structure)
    db_session.add(polymer); db_session.commit()
    assert structure.validation_status == "not_validated" and structure.validated_at is None
    raw = structure.representation
    apply_result(structure); db_session.commit(); apply_result(structure); db_session.commit()
    assert structure.representation == raw and structure.validation_status == "valid"
    structure.validation_status = "unknown"
    try:
        db_session.commit()
        assert False, "database check constraint should reject unknown validation status"
    except IntegrityError:
        db_session.rollback()
