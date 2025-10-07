"""prune legacy employee text fields and add absolute photo urls placeholder

Revision ID: 20251007_200000
Revises: 8d9a4b7c2f13
Create Date: 2025-10-07 20:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '20251007_200000'
down_revision = '8d9a4b7c2f13'
branch_labels = None
depends_on = None

def _has_column(bind, table: str, column: str) -> bool:
    insp = sa.inspect(bind)
    try:
        return column in [c['name'] for c in insp.get_columns(table)]
    except Exception:
        return False

def upgrade():
    bind = op.get_bind()
    # Drop legacy columns if they still exist
    for col in ['department', 'position', 'photo_url', 'face_encoding']:
        if _has_column(bind, 'employees', col):
            try:
                op.drop_column('employees', col)
            except Exception:
                pass


def downgrade():
    # Cannot reliably restore dropped columns with data; create empty nullable columns for reversibility
    for name, coltype in [
        ('department', sa.String(length=100)),
        ('position', sa.String(length=100)),
        ('photo_url', sa.String(length=500)),
        ('face_encoding', sa.Text()),
    ]:
        try:
            op.add_column('employees', sa.Column(name, coltype, nullable=True))
        except Exception:
            pass
