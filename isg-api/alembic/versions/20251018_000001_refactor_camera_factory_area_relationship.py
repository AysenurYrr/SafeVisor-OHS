"""Refactor camera-factory area relationship to one-to-many

Revision ID: 20251018_000001
Revises: 
Create Date: 2025-10-18 20:40:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251018_000001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add factory_area_id column to cameras table
    op.add_column('cameras', sa.Column('factory_area_id', sa.Integer(), nullable=True))
    op.create_index('ix_cameras_factory_area_id', 'cameras', ['factory_area_id'])
    op.create_foreign_key(
        'fk_cameras_factory_area_id', 
        'cameras', 
        'factory_areas', 
        ['factory_area_id'], 
        ['id'], 
        ondelete='SET NULL'
    )
    
    # Migrate data from area_cameras junction table to factory_area_id column
    # This will take the first area assignment for each camera
    op.execute('''
        UPDATE cameras 
        SET factory_area_id = (
            SELECT area_id 
            FROM area_cameras 
            WHERE area_cameras.camera_id = cameras.id 
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM area_cameras WHERE area_cameras.camera_id = cameras.id
        )
    ''')
    
    # Drop the area_cameras junction table
    op.drop_table('area_cameras')


def downgrade():
    # Recreate area_cameras junction table
    op.create_table(
        'area_cameras',
        sa.Column('area_id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['area_id'], ['factory_areas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('area_id', 'camera_id')
    )
    
    # Migrate data back from factory_area_id to area_cameras
    op.execute('''
        INSERT INTO area_cameras (area_id, camera_id)
        SELECT factory_area_id, id
        FROM cameras
        WHERE factory_area_id IS NOT NULL
    ''')
    
    # Drop factory_area_id column and its constraints
    op.drop_constraint('fk_cameras_factory_area_id', 'cameras', type_='foreignkey')
    op.drop_index('ix_cameras_factory_area_id', 'cameras')
    op.drop_column('cameras', 'factory_area_id')
