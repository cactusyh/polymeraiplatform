"""Phase 2.1 integrity tests, executed against SQLite with foreign keys enabled."""

import pytest
from pydantic import ValidationError
from sqlalchemy import delete, text
from sqlalchemy.exc import IntegrityError

from backend.app.models import Polymer, PolymerStructure, PropertyDefinition, PropertyRecord, Provenance
from backend.app.schemas.polymer import PolymerCreate, PolymerStructureCreate, PropertyRecordCreate
from backend.app.seed_examples import POLYMER_EXAMPLES


def _record_graph(db_session):
    polymer = Polymer(name="Polyethylene", canonical_name="polyethylene", architecture="homopolymer")
    structure = PolymerStructure(polymer=polymer, representation_type="psmiles", representation="[*]CC[*]")
    definition = PropertyDefinition(key="density", name="Density", symbol="rho", canonical_unit="g/cm^3", category="physical")
    provenance = Provenance(source_type="manual", notes="synthetic fixture for software testing only")
    db_session.add_all([polymer, structure, definition, provenance])
    db_session.flush()
    record = PropertyRecord(polymer_id=polymer.id, property_definition_id=definition.id, value=1.0, unit="g/cm^3", provenance_type="experiment", provenance_id=provenance.id)
    db_session.add(record)
    db_session.commit()
    return polymer, structure, definition, provenance, record


def test_sqlite_foreign_keys_are_enabled(db_session) -> None:
    assert db_session.execute(text("PRAGMA foreign_keys")).scalar_one() == 1


def test_database_polymer_delete_cascades_structures_and_property_records(db_session) -> None:
    polymer, structure, _definition, _provenance, record = _record_graph(db_session)
    structure_id, record_id = structure.id, record.id
    db_session.execute(delete(Polymer).where(Polymer.id == polymer.id))
    db_session.commit()
    assert db_session.get(PolymerStructure, structure_id) is None
    assert db_session.get(PropertyRecord, record_id) is None


@pytest.mark.parametrize("target_name", ["definition", "provenance"])
def test_referenced_scientific_metadata_delete_is_restricted(db_session, target_name) -> None:
    _polymer, _structure, definition, provenance, _record = _record_graph(db_session)
    db_session.delete(definition if target_name == "definition" else provenance)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


@pytest.mark.parametrize("field", ["number_average_molecular_weight", "weight_average_molecular_weight", "dispersity", "degree_of_polymerization"])
def test_invalid_polymer_metadata_rejected_by_schema(field) -> None:
    with pytest.raises(ValidationError):
        PolymerCreate.model_validate({"name": "x", field: 0})


@pytest.mark.parametrize("field", ["number_average_molecular_weight", "weight_average_molecular_weight", "dispersity", "degree_of_polymerization"])
def test_invalid_polymer_metadata_rejected_by_database(db_session, field) -> None:
    polymer = Polymer(name=f"invalid-{field}", canonical_name=f"invalid-{field}", architecture="homopolymer", **{field: -1})
    db_session.add(polymer)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_uncertainty_and_property_values_validate_scientifically() -> None:
    with pytest.raises(ValidationError):
        PropertyRecordCreate(property_definition_id="00000000-0000-0000-0000-000000000001", value=1.0, unit="K", uncertainty=-0.1)
    assert PropertyRecordCreate(property_definition_id="00000000-0000-0000-0000-000000000001", value=0.0, unit="K", uncertainty=0.0).value == 0.0
    assert PropertyRecordCreate(property_definition_id="00000000-0000-0000-0000-000000000001", value=-2.5, unit="eV").value == -2.5


def test_negative_uncertainty_is_rejected_by_database(db_session) -> None:
    polymer, _structure, definition, _provenance, _record = _record_graph(db_session)
    db_session.add(PropertyRecord(polymer_id=polymer.id, property_definition_id=definition.id, value=0.0, unit="K", uncertainty=-0.1, provenance_type="unknown"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_whitespace_canonical_name_is_rejected_and_omission_uses_name(client) -> None:
    assert client.post("/api/v1/polymers", json={"name": "Valid", "canonical_name": "   "}).status_code == 422
    created = client.post("/api/v1/polymers", json={"name": "  Polyethylene  "}).json()
    assert created["canonical_name"] == "Polyethylene"


def test_empty_structure_rejected_and_examples_do_not_claim_canonicalization() -> None:
    with pytest.raises(ValidationError):
        PolymerStructureCreate(representation_type="psmiles", representation="   ")
    assert all(not structure["is_canonical"] for polymer in POLYMER_EXAMPLES for structure in polymer["structures"])


def test_minimal_api_serializes_provenance_explicitly(client, db_session) -> None:
    definition_response = client.post("/api/v1/property-definitions", json={"key": "glass_transition_temperature", "name": "Glass transition temperature", "symbol": "Tg", "canonical_unit": "K", "category": "thermal"})
    polymer_response = client.post("/api/v1/polymers", json={"name": "Polystyrene", "architecture": "homopolymer", "structures": [{"representation_type": "psmiles", "representation": " [*]CC([*])c1ccccc1 ", "is_canonical": False}]})
    provenance = Provenance(source_type="manual", notes="Synthetic fixture for software testing only")
    db_session.add(provenance); db_session.commit()
    response = client.post(f"/api/v1/polymers/{polymer_response.json()['id']}/properties", json={"property_definition_id": definition_response.json()["id"], "value": 373.0, "unit": "K", "uncertainty": 5.0, "provenance_type": "experiment", "method": "DSC", "conditions": {"heating_rate_K_per_min": 10}, "provenance_id": str(provenance.id)})
    assert response.status_code == 201
    assert response.json()["property"]["key"] == "glass_transition_temperature"
    assert response.json()["provenance"]["source_type"] == "manual"
