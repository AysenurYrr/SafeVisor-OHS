"""Add new fields to employees and cameras, create violation_logs and analytics tables

Revision ID: 20250926_2022_add_new_fields_and_tables
Revises: 20250922_000001_add_uuid_to_employees
Create Date: 2025-09-26 20:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20250926_2022_add_new_fields_and_tables'
down_revision = '20250922_000001_add_uuid_to_employees'
branch_labels = None
depends_on = None


def _has_column(connection, table: str, column: str) -> bool:
    """Check if column exists in table"""
    inspector = sa.inspect(connection)
    try:
        cols = [c["name"] for c in inspector.get_columns(table)]
        return column in cols
    except Exception:
        return False


def _has_table(connection, table_name: str) -> bool:
    """Check if table exists"""
    inspector = sa.inspect(connection)
    try:
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    
    # Add new fields to employees table
    if not _has_column(bind, "employees", "violation_score"):
        op.add_column('employees', sa.Column('violation_score', sa.Float(), nullable=False, server_default='0'))
    
    if not _has_column(bind, "employees", "photo_1_path"):
        op.add_column('employees', sa.Column('photo_1_path', sa.String(500), nullable=True))
    
    if not _has_column(bind, "employees", "photo_2_path"):
        op.add_column('employees', sa.Column('photo_2_path', sa.String(500), nullable=True))
    
    if not _has_column(bind, "employees", "photo_3_path"):
        op.add_column('employees', sa.Column('photo_3_path', sa.String(500), nullable=True))
    
    if not _has_column(bind, "employees", "face_embeddings"):
        op.add_column('employees', sa.Column('face_embeddings', JSONB, nullable=True))
    
    # Add new fields to cameras table
    if not _has_column(bind, "cameras", "stream_path"):
        # Add stream_path column, copy from stream_url for backward compatibility
        op.add_column('cameras', sa.Column('stream_path', sa.String(500), nullable=True))
        # Update stream_path with stream_url values
        bind.execute(text("UPDATE cameras SET stream_path = stream_url WHERE stream_path IS NULL"))
        # Make it not null after updating
        op.alter_column('cameras', 'stream_path', nullable=False)
    
    if not _has_column(bind, "cameras", "violation_rules"):
        op.add_column('cameras', sa.Column('violation_rules', JSONB, nullable=True))
    
    if not _has_column(bind, "cameras", "status"):
        op.add_column('cameras', sa.Column('status', sa.Enum('ONLINE', 'OFFLINE', 'UNKNOWN', name='camerastatus'), nullable=False, server_default='UNKNOWN'))
    
    # Add unique constraint to cameras.name if it doesn't exist
    try:
        op.create_unique_constraint('uq_cameras_name', 'cameras', ['name'])
    except Exception:
        # Constraint might already exist, ignore
        pass
    
    # Create violation_logs table
    if not _has_table(bind, "violation_logs"):
        op.create_table('violation_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('employee_id', sa.Integer(), nullable=True),
            sa.Column('camera_id', sa.Integer(), nullable=False),
            sa.Column('violation_types', JSONB, nullable=False),
            sa.Column('image_paths', JSONB, nullable=True),
            sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('duration', sa.Float(), nullable=True),
            sa.Column('reported', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('bounding_boxes', JSONB, nullable=True),
            sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
            sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_violation_logs_id'), 'violation_logs', ['id'], unique=False)
        op.create_index('ix_violation_logs_employee_id', 'violation_logs', ['employee_id'], unique=False)
        op.create_index('ix_violation_logs_camera_id', 'violation_logs', ['camera_id'], unique=False)
        op.create_index('ix_violation_logs_timestamp', 'violation_logs', ['timestamp'], unique=False)
        op.create_index('ix_violation_logs_employee_timestamp', 'violation_logs', ['employee_id', 'timestamp'], unique=False)
        op.create_index('ix_violation_logs_camera_timestamp', 'violation_logs', ['camera_id', 'timestamp'], unique=False)
        op.create_index('ix_violation_logs_reported', 'violation_logs', ['reported'], unique=False)
    
    # Create analytics table
    if not _has_table(bind, "analytics"):
        op.create_table('analytics',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('employee_id', sa.Integer(), nullable=False),
            sa.Column('violation_type', sa.String(100), nullable=False),
            sa.Column('violation_date', sa.Date(), nullable=False),
            sa.Column('violation_image_path', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_analytics_id'), 'analytics', ['id'], unique=False)
        op.create_index('ix_analytics_employee_id', 'analytics', ['employee_id'], unique=False)
        op.create_index('ix_analytics_violation_type', 'analytics', ['violation_type'], unique=False)
        op.create_index('ix_analytics_date', 'analytics', ['violation_date'], unique=False)
        op.create_index('ix_analytics_employee_date', 'analytics', ['employee_id', 'violation_date'], unique=False)
        op.create_index('ix_analytics_created_at', 'analytics', ['created_at'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    
    # Drop analytics table
    if _has_table(bind, "analytics"):
        op.drop_index('ix_analytics_created_at', table_name='analytics')
        op.drop_index('ix_analytics_employee_date', table_name='analytics')
        op.drop_index('ix_analytics_date', table_name='analytics')
        op.drop_index('ix_analytics_violation_type', table_name='analytics')
        op.drop_index('ix_analytics_employee_id', table_name='analytics')
        op.drop_index(op.f('ix_analytics_id'), table_name='analytics')
        op.drop_table('analytics')
    
    # Drop violation_logs table
    if _has_table(bind, "violation_logs"):
        op.drop_index('ix_violation_logs_reported', table_name='violation_logs')
        op.drop_index('ix_violation_logs_camera_timestamp', table_name='violation_logs')
        op.drop_index('ix_violation_logs_employee_timestamp', table_name='violation_logs')
        op.drop_index('ix_violation_logs_timestamp', table_name='violation_logs')
        op.drop_index('ix_violation_logs_camera_id', table_name='violation_logs')
        op.drop_index('ix_violation_logs_employee_id', table_name='violation_logs')
        op.drop_index(op.f('ix_violation_logs_id'), table_name='violation_logs')
        op.drop_table('violation_logs')
    
    # Remove fields from cameras table
    try:
        op.drop_constraint('uq_cameras_name', 'cameras', type_='unique')
    except Exception:
        pass
    
    if _has_column(bind, "cameras", "status"):
        op.drop_column('cameras', 'status')
        # Drop enum type
        try:
            bind.execute(text("DROP TYPE IF EXISTS camerastatus"))
        except Exception:
            pass
    
    if _has_column(bind, "cameras", "violation_rules"):
        op.drop_column('cameras', 'violation_rules')
    
    if _has_column(bind, "cameras", "stream_path"):
        op.drop_column('cameras', 'stream_path')
    
    # Remove fields from employees table
    if _has_column(bind, "employees", "face_embeddings"):
        op.drop_column('employees', 'face_embeddings')
    
    if _has_column(bind, "employees", "photo_3_path"):
        op.drop_column('employees', 'photo_3_path')
    
    if _has_column(bind, "employees", "photo_2_path"):
        op.drop_column('employees', 'photo_2_path')
    
    if _has_column(bind, "employees", "photo_1_path"):
        op.drop_column('employees', 'photo_1_path')
    
    if _has_column(bind, "employees", "violation_score"):
        op.drop_column('employees', 'violation_score')