"""Phase 2 scientific model and API integration tests using SQLite."""

import pytest
from pydantic import ValidationError

from backend.app.models import Polymer, PropertyDefinition, PropertyRecord, Provenance
from backend.app.schemas.polymer import PolymerCreate, PolymerStructureCreate


def test_polymer_structure_relationship_and_cascade(db_session) -> None:
    polymer = Polymer(name="Polystyrene", canonical_name="polystyrene", architecture="homopolymer")
    polymer.structures = [
        __import__("backend.app.models", fromlist=["PolymerStructure"]).PolymerStructure(
            representation_type="psmiles", representation="[*]CC([*])c1ccccc1", is_canonical=True
        )
    ]
    db_session.add(polymer)
    db_session.commit()
    polymer_id = polymer.id
    assert len(polymer.structures) == 1
    db_session.delete(polymer)
    db_session.commit()
    assert db_session.get(Polymer, polymer_id) is None


def test_property_record_has_definition_and_provenance(db_session) -> None:
    polymer = Polymer(name="Polyethylene", canonical_name="polyethylene", architecture="homopolymer")
    definition = PropertyDefinition(key="density", name="Density", symbol="rho", canonical_unit="g/cm^3", category="physical")
    provenance = Provenance(source_type="manual", notes="synthetic fixture for software testing only")
    db_session.add_all([polymer, definition, provenance])
    db_session.commit()
    record = PropertyRecord(polymer_id=polymer.id, property_definition_id=definition.id, value=1.0, unit="g/cm^3", provenance_type="experiment", provenance_id=provenance.id)
    db_session.add(record)
    db_session.commit()
    assert record.property_definition.key == "density"
    assert record.provenance.source_type == "manual"


@pytest.mark.parametrize("payload", [
    {"name": "x", "number_average_molecular_weight": 0},
    {"name": "x", "weight_average_molecular_weight": -1},
])
def test_invalid_molecular_weight_rejected(payload) -> None:
    with pytest.raises(ValidationError):
        PolymerCreate.model_validate(payload)


def test_invalid_dispersity_and_empty_structure_rejected() -> None:
    with pytest.raises(ValidationError):
        PolymerCreate(name="x", dispersity=0)
    with pytest.raises(ValidationError):
        PolymerStructureCreate(representation_type="psmiles", representation="   ")


def test_minimal_api_serializes_provenance_explicitly(client, db_session) -> None:
    definition_response = client.post("/api/v1/property-definitions", json={"key": "glass_transition_temperature", "name": "Glass transition temperature", "symbol": "Tg", "canonical_unit": "K", "category": "thermal"})
    assert definition_response.status_code == 201
    polymer_response = client.post("/api/v1/polymers", json={"name": "Polystyrene", "architecture": "homopolymer", "structures": [{"representation_type": "psmiles", "representation": " [*]CC([*])c1ccccc1 ", "is_canonical": True}]})
    assert polymer_response.status_code == 201
    polymer = polymer_response.json()
    assert polymer["structures"][0]["representation"] == "[*]CC([*])c1ccccc1"
    provenance = Provenance(source_type="manual", notes="Synthetic fixture for software testing only")
    db_session.add(provenance)
    db_session.commit()
    record_response = client.post(f"/api/v1/polymers/{polymer['id']}/properties", json={"property_definition_id": definition_response.json()["id"], "value": 373.0, "unit": "K", "uncertainty": 5.0, "provenance_type": "experiment", "method": "DSC", "conditions": {"heating_rate_K_per_min": 10}, "provenance_id": str(provenance.id)})
    assert record_response.status_code == 201
    body = record_response.json()
    assert body["property"]["key"] == "glass_transition_temperature"
    assert body["provenance_type"] == "experiment"
    assert body["provenance"]["source_type"] == "manual"
    retrieved = client.get(f"/api/v1/polymers/{polymer['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["property_records"][0]["provenance"]["notes"] == "Synthetic fixture for software testing only"


def test_api_rejects_invalid_provenance_type_and_empty_unit(client) -> None:
    response = client.post("/api/v1/property-definitions", json={"key": "band_gap", "name": "Band gap", "canonical_unit": "eV"})
    assert response.status_code == 201
    polymer = client.post("/api/v1/polymers", json={"name": "Polyethylene", "architecture": "homopolymer"}).json()
    invalid = client.post(f"/api/v1/polymers/{polymer['id']}/properties", json={"property_definition_id": response.json()["id"], "value": 0.0, "unit": " ", "provenance_type": "claimed_fact"})
    assert invalid.status_code == 422
