"""add persisted cheminformatics metadata

Revision ID: 20260919_04
Revises: 20260919_03
"""
from alembic import op
import sqlalchemy as sa
revision="20260919_04";down_revision="20260919_03";branch_labels=None;depends_on=None
def upgrade():
 with op.batch_alter_table("polymer_structures") as b:
  b.add_column(sa.Column("validation_status",sa.String(32),nullable=False,server_default="not_validated"));b.add_column(sa.Column("validation_message",sa.Text()));b.add_column(sa.Column("normalized_representation",sa.String(4096)));b.add_column(sa.Column("connection_point_count",sa.Integer()));b.add_column(sa.Column("normalization_version",sa.String(64)));b.add_column(sa.Column("rdkit_version",sa.String(64)));b.add_column(sa.Column("validated_at",sa.DateTime(timezone=True)));b.add_column(sa.Column("derived_properties",sa.JSON()))
 op.create_index("ix_polymer_structures_validation_status","polymer_structures",["validation_status"]);op.create_index("ix_polymer_structures_normalized_representation","polymer_structures",["normalized_representation"])
def downgrade():
 op.drop_index("ix_polymer_structures_normalized_representation",table_name="polymer_structures");op.drop_index("ix_polymer_structures_validation_status",table_name="polymer_structures")
 with op.batch_alter_table("polymer_structures") as b:
  [b.drop_column(c) for c in ["derived_properties","validated_at","rdkit_version","normalization_version","connection_point_count","normalized_representation","validation_message","validation_status"]]
