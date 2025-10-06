"""rename face_embeddings to face_embedding (or create)

Revision ID: 20251007_121500
Revises: 20251007_120000_add_face_embedding_column
Create Date: 2025-10-07 12:15:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20251007_121500'
down_revision = '20251007_120000_add_face_embedding_column'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('employees')]
    # If legacy plural column exists, rename it
    if 'face_embeddings' in cols and 'face_embedding' not in cols:
        op.alter_column('employees', 'face_embeddings', new_column_name='face_embedding')
    else:
        # If neither plural nor singular exists (fresh DB), ensure singular column is present
        if 'face_embedding' not in cols:
            op.add_column('employees', sa.Column('face_embedding', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('employees')]
    if 'face_embedding' in cols and 'face_embeddings' not in cols:
        # Downgrade by renaming back to plural for backward compatibility
        op.alter_column('employees', 'face_embedding', new_column_name='face_embeddings')