"""
Add photo paths and violation_score to employees table

Revision ID: 20250115_000001
Revises: 20250922_000001
Create Date: 2025-01-15 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
# Shortened revision & updated down_revision to shortened prior id.
revision = "20250115_000001"
down_revision = "20250922_000001"
branch_labels = None
depends_on = None


def _has_column(connection, table: str, column: str) -> bool:
    inspector = sa.inspect(connection)
    cols = [c["name"] for c in inspector.get_columns(table)]
    return column in cols


def upgrade() -> None:
    bind = op.get_bind()
    
    # Add photo_front_path if it doesn't exist
    if not _has_column(bind, "employees", "photo_front_path"):
        op.add_column(
            "employees",
            sa.Column("photo_front_path", sa.String(500), nullable=True)
        )
    
    # Add photo_left_path if it doesn't exist
    if not _has_column(bind, "employees", "photo_left_path"):
        op.add_column(
            "employees",
            sa.Column("photo_left_path", sa.String(500), nullable=True)
        )
    
    # Add photo_right_path if it doesn't exist
    if not _has_column(bind, "employees", "photo_right_path"):
        op.add_column(
            "employees",
            sa.Column("photo_right_path", sa.String(500), nullable=True)
        )
    
    # Add violation_score if it doesn't exist
    if not _has_column(bind, "employees", "violation_score"):
        op.add_column(
            "employees",
            sa.Column("violation_score", sa.Integer, nullable=False, server_default="0")
        )


def downgrade() -> None:
    bind = op.get_bind()
    
    # Drop violation_score if it exists
    if _has_column(bind, "employees", "violation_score"):
        op.drop_column("employees", "violation_score")
    
    # Drop photo_right_path if it exists
    if _has_column(bind, "employees", "photo_right_path"):
        op.drop_column("employees", "photo_right_path")
    
    # Drop photo_left_path if it exists
    if _has_column(bind, "employees", "photo_left_path"):
        op.drop_column("employees", "photo_left_path")
    
    # Drop photo_front_path if it exists
    if _has_column(bind, "employees", "photo_front_path"):
        op.drop_column("employees", "photo_front_path")
