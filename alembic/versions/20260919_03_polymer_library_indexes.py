"""add indexes for polymer library query paths

Revision ID: 20260919_03
Revises: 20260919_02
"""
from alembic import op

revision="20260919_03"
down_revision="20260919_02"
branch_labels=None
depends_on=None
def upgrade()->None:
    op.create_index("ix_polymers_name","polymers",["name"])
    op.create_index("ix_polymers_polymer_class","polymers",["polymer_class"])
    op.create_index("ix_polymers_architecture","polymers",["architecture"])
    op.create_index("ix_property_definitions_category","property_definitions",["category"])
    op.create_index("ix_property_records_provenance_type","property_records",["provenance_type"])
def downgrade()->None:
    op.drop_index("ix_property_records_provenance_type",table_name="property_records")
    op.drop_index("ix_property_definitions_category",table_name="property_definitions")
    op.drop_index("ix_polymers_architecture",table_name="polymers")
    op.drop_index("ix_polymers_polymer_class",table_name="polymers")
    op.drop_index("ix_polymers_name",table_name="polymers")
