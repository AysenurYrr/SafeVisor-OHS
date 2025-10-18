"""Merge migration branches

Revision ID: d7fe0aefe4c0
Revises: 20251007_200000, 20251018_000001
Create Date: 2025-10-18 21:13:54.222070+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7fe0aefe4c0'
down_revision = ('20251007_200000', '20251018_000001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass