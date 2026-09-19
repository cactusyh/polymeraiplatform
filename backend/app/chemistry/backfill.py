"""Repeatable command for deriving chemistry metadata on stored structures."""
from backend.app.chemistry.service import VALIDATION_STATUSES, process
from backend.app.db.session import SessionLocal
from backend.app.models import PolymerStructure


def apply_result(structure: PolymerStructure) -> str:
    """Process one structure without modifying its raw representation."""
    result = process(structure.representation_type, structure.representation)
    structure.validation_status = result.status
    structure.validation_message = "; ".join(result.warnings) if result.warnings else result.validation_message
    structure.normalized_representation = result.normalized_representation
    structure.connection_point_count = result.connection_point_count
    structure.normalization_version = result.normalization_version
    structure.rdkit_version = result.rdkit_version
    structure.validated_at = result.validated_at
    structure.derived_properties = result.derived_properties
    return result.status


def main() -> None:
    db = SessionLocal()
    counts = {status: 0 for status in VALIDATION_STATUSES if status != "not_validated"}
    try:
        for structure in db.query(PolymerStructure).order_by(PolymerStructure.id):
            counts[apply_result(structure)] += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(" ".join(f"{status}={counts[status]}" for status in sorted(counts)))


if __name__ == "__main__":
    main()
