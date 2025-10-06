"""
Add factory_areas table with cameras and safety rules associations

Revision ID: 20250107_000001
Revises: 20251007_121500
Create Date: 2025-01-07 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "20250107_000001_add_factory_areas"
down_revision = "20251007_121500_rename_face_embeddings_column"
branch_labels = None
depends_on = None


def _table_exists(connection, table_name: str) -> bool:
    inspector = sa.inspect(connection)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    
    # Create factory_areas table if it doesn't exist
    if not _table_exists(bind, "factory_areas"):
        op.create_table(
            "factory_areas",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
            sa.Column("created_by", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_factory_areas_created_by"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name", name="uq_factory_areas_name")
        )
        op.create_index("ix_factory_areas_id", "factory_areas", ["id"], unique=False)
        op.create_index("ix_factory_areas_name", "factory_areas", ["name"], unique=False)
    
    # Create area_cameras association table if it doesn't exist
    if not _table_exists(bind, "area_cameras"):
        op.create_table(
            "area_cameras",
            sa.Column("area_id", sa.Integer(), nullable=False),
            sa.Column("camera_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["area_id"], ["factory_areas.id"], ondelete="CASCADE", name="fk_area_cameras_area_id"),
            sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"], ondelete="CASCADE", name="fk_area_cameras_camera_id"),
            sa.PrimaryKeyConstraint("area_id", "camera_id")
        )
    
    # Create area_rules association table if it doesn't exist
    if not _table_exists(bind, "area_rules"):
        op.create_table(
            "area_rules",
            sa.Column("area_id", sa.Integer(), nullable=False),
            sa.Column("rule_name", sa.String(length=50), nullable=False),
            sa.ForeignKeyConstraint(["area_id"], ["factory_areas.id"], ondelete="CASCADE", name="fk_area_rules_area_id"),
            sa.PrimaryKeyConstraint("area_id", "rule_name")
        )


def downgrade() -> None:
    bind = op.get_bind()
    
    # Drop tables in reverse order
    if _table_exists(bind, "area_rules"):
        op.drop_table("area_rules")
    
    if _table_exists(bind, "area_cameras"):
        op.drop_table("area_cameras")
    
    if _table_exists(bind, "factory_areas"):
        op.drop_index("ix_factory_areas_name", table_name="factory_areas")
        op.drop_index("ix_factory_areas_id", table_name="factory_areas")
        op.drop_table("factory_areas")
