"""RDKit-backed, attachment-aware repeat-unit chemistry processing.

Raw structure text is provenance data and is never altered. Normalization,
descriptors, and fingerprints are derived metadata for supported checks only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal, TypeAlias

from rdkit import Chem, rdBase
from rdkit.Chem import DataStructs, Descriptors, rdFingerprintGenerator
from rdkit.DataStructs.cDataStructs import ExplicitBitVect

SUPPORTED_REPRESENTATION_TYPES = frozenset({"smiles", "psmiles", "repeat_unit_smiles"})
VALIDATION_STATUSES = frozenset(
    {"not_validated", "valid", "partially_valid", "invalid", "unsupported"}
)
NORMALIZATION_VERSION = "phase4-v1"
FINGERPRINT_CONFIG = {
    "algorithm": "Morgan",
    "radius": 2,
    "n_bits": 2048,
    "attachment_handling": "wildcards_retained",
}
ValidationStatus: TypeAlias = Literal[
    "not_validated", "valid", "partially_valid", "invalid", "unsupported"
]


class ChemistryProcessingError(ValueError):
    """A chemistry operation could not produce the required result."""


@dataclass(frozen=True)
class ChemistryProcessingResult:
    """Derived chemistry metadata for one processing attempt."""

    status: ValidationStatus
    validation_message: str | None
    normalized_representation: str | None
    connection_point_count: int | None
    warnings: list[str]
    derived_properties: dict[str, float | int] | None
    rdkit_version: str | None
    normalization_version: str | None
    validated_at: datetime | None

    def metadata(self) -> dict[str, object]:
        """Return persisted fields while omitting transient warnings."""
        data = asdict(self)
        data.pop("warnings")
        return data


def process(representation_type: str, representation: str) -> ChemistryProcessingResult:
    """Validate and derive metadata while preserving raw source text unchanged."""
    processed_at = datetime.now(timezone.utc)
    if representation_type not in SUPPORTED_REPRESENTATION_TYPES:
        return _unavailable_result(
            "unsupported",
            "Representation type is stored but not supported by the chemistry engine.",
            processed_at,
        )

    molecule = Chem.MolFromSmiles(representation)
    if molecule is None:
        return _unavailable_result(
            "invalid",
            "Unable to parse the supplied structure representation.",
            processed_at,
        )

    connection_point_count = sum(atom.GetAtomicNum() == 0 for atom in molecule.GetAtoms())
    warnings: list[str] = []
    status: ValidationStatus = "valid"
    if representation_type == "psmiles" and connection_point_count != 2:
        status = "partially_valid"
        warnings.append(
            f"Connection-point count is {connection_point_count}; "
            "current checks do not require exactly two."
        )

    return ChemistryProcessingResult(
        status=status,
        validation_message=None,
        normalized_representation=Chem.MolToSmiles(molecule, canonical=True),
        connection_point_count=connection_point_count,
        warnings=warnings,
        derived_properties=_descriptors(molecule),
        rdkit_version=rdBase.rdkitVersion,
        normalization_version=NORMALIZATION_VERSION,
        validated_at=processed_at,
    )


def _unavailable_result(
    status: Literal["invalid", "unsupported"],
    validation_message: str,
    processed_at: datetime,
) -> ChemistryProcessingResult:
    return ChemistryProcessingResult(
        status=status,
        validation_message=validation_message,
        normalized_representation=None,
        connection_point_count=None,
        warnings=[],
        derived_properties=None,
        rdkit_version=rdBase.rdkitVersion,
        normalization_version=NORMALIZATION_VERSION,
        validated_at=processed_at,
    )


def _descriptors(molecule: Chem.Mol) -> dict[str, float | int]:
    return {
        "heavy_atom_count": molecule.GetNumHeavyAtoms(),
        "heteroatom_count": sum(
            atom.GetAtomicNum() not in (0, 1, 6) for atom in molecule.GetAtoms()
        ),
        "ring_count": molecule.GetRingInfo().NumRings(),
        "aromatic_ring_count": sum(
            all(molecule.GetAtomWithIdx(index).GetIsAromatic() for index in ring)
            for ring in molecule.GetRingInfo().AtomRings()
        ),
        "rotatable_bond_count": Descriptors.NumRotatableBonds(molecule),
        "fraction_csp3": Descriptors.FractionCSP3(molecule),
    }


def fingerprint(normalized_representation: str) -> ExplicitBitVect:
    """Create Morgan radius-2 / 2048-bit fingerprint retaining wildcard atoms."""
    molecule = Chem.MolFromSmiles(normalized_representation)
    if molecule is None:
        raise ChemistryProcessingError("A fingerprint could not be generated for this structure.")

    try:
        generator = rdFingerprintGenerator.GetMorganGenerator(
            radius=FINGERPRINT_CONFIG["radius"],
            fpSize=FINGERPRINT_CONFIG["n_bits"],
        )
        return generator.GetFingerprint(molecule)
    except Exception as error:
        raise ChemistryProcessingError(
            "A fingerprint could not be generated for this structure."
        ) from error


def similarity(left: str, right: str) -> float:
    """Return Tanimoto repeat-unit structural similarity for normalized inputs."""
    return DataStructs.TanimotoSimilarity(fingerprint(left), fingerprint(right))
