"""Clearly labelled example data for development or documentation.

These records are not inserted automatically and do not claim experimental values
or platform-verified chemical canonicalization.
"""

PROPERTY_DEFINITION_EXAMPLES = (
    {"key": "glass_transition_temperature", "name": "Glass transition temperature", "symbol": "Tg", "canonical_unit": "K", "category": "thermal"},
    {"key": "density", "name": "Density", "symbol": "rho", "canonical_unit": "g/cm^3", "category": "physical"},
    {"key": "band_gap", "name": "Band gap", "symbol": "Eg", "canonical_unit": "eV", "category": "electronic"},
)

POLYMER_EXAMPLES = (
    {"name": "Polystyrene", "canonical_name": "polystyrene", "polymer_class": "polystyrene", "architecture": "homopolymer", "structures": [{"representation_type": "psmiles", "representation": "[*]CC([*])c1ccccc1", "is_canonical": False, "source": "example fixture; not chemically validated or canonicalized by the platform"}]},
    {"name": "Polyethylene", "canonical_name": "polyethylene", "polymer_class": "polyolefin", "architecture": "homopolymer", "structures": [{"representation_type": "psmiles", "representation": "[*]CC[*]", "is_canonical": False, "source": "example fixture; not chemically validated or canonicalized by the platform"}]},
    {"name": "Poly(ethylene oxide)", "canonical_name": "polyethylene_oxide", "polymer_class": "polyether", "architecture": "homopolymer", "structures": [{"representation_type": "psmiles", "representation": "[*]CCO[*]", "is_canonical": False, "source": "example fixture; not chemically validated or canonicalized by the platform"}]},
)

SYNTHETIC_TEST_PROVENANCE = {"source_type": "manual", "title": "Synthetic software test fixture", "notes": "Synthetic fixture for software testing only; not experimental reference data."}
