"""add face_embedding column

Revision ID: 20251007_120000
Revises: 20250926_2022_add_new_fields_and_tables
Create Date: 2025-10-07 12:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20251007_120000'
down_revision = '20250926_2022_add_new_fields_and_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add JSONB column for face embedding if not exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('employees')]
    if 'face_embedding' not in cols:
        op.add_column('employees', sa.Column('face_embedding', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('employees')]
    if 'face_embedding' in cols:
        op.drop_column('employees', 'face_embedding')