"""Add evidence and tracking fields to violations

Revision ID: temporal_tracking_001
Revises: 53f876f7612e
Create Date: 2025-10-18 22:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'temporal_tracking_001'
down_revision = '53f876f7612e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add evidence and tracking fields to violations table."""
    # Add evidence image columns
    op.add_column('violations', 
                  sa.Column('evidence_start_image', sa.String(500), nullable=True))
    op.add_column('violations', 
                  sa.Column('evidence_middle_image', sa.String(500), nullable=True))
    op.add_column('violations', 
                  sa.Column('evidence_end_image', sa.String(500), nullable=True))
    
    # Add tracking columns
    op.add_column('violations', 
                  sa.Column('person_tracker_id', sa.Integer(), nullable=True))
    op.add_column('violations', 
                  sa.Column('duration_frames', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove evidence and tracking fields from violations table."""
    # Remove tracking columns
    op.drop_column('violations', 'duration_frames')
    op.drop_column('violations', 'person_tracker_id')
    
    # Remove evidence image columns
    op.drop_column('violations', 'evidence_end_image')
    op.drop_column('violations', 'evidence_middle_image')
    op.drop_column('violations', 'evidence_start_image')
