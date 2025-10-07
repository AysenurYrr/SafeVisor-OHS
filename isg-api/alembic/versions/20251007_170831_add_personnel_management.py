"""add personnel management tables

Revision ID: 20251007_170831
Revises: 20251007_121500
Create Date: 2025-10-07 17:08:31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
# Normalized (removed filename suffix) to keep consistent chain.
revision = '20251007_170831'
down_revision = '20251007_121500'
branch_labels = None
depends_on = None


def _has_table(bind, name: str) -> bool:
    return name in inspect(bind).get_table_names()

def _has_column(bind, table: str, column: str) -> bool:
    insp = inspect(bind)
    try:
        return column in [c['name'] for c in insp.get_columns(table)]
    except Exception:
        return False

def upgrade():
    bind = op.get_bind()

    # Departments
    if not _has_table(bind, 'departments'):
        op.create_table(
            'departments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
        op.create_index(op.f('ix_departments_name'), 'departments', ['name'], unique=True)

    # Positions
    if not _has_table(bind, 'positions'):
        op.create_table(
            'positions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('department_id', sa.Integer(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_positions_id'), 'positions', ['id'], unique=False)
        op.create_index(op.f('ix_positions_name'), 'positions', ['name'], unique=False)

    # Employee Logs
    if not _has_table(bind, 'employee_logs'):
        op.create_table(
            'employee_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('employee_id', sa.Integer(), nullable=False),
            sa.Column('action', sa.String(length=50), nullable=False),
            sa.Column('actor_id', sa.Integer(), nullable=True),
            sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('details', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
            sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_employee_logs_id'), 'employee_logs', ['id'], unique=False)
        op.create_index(op.f('ix_employee_logs_employee_id'), 'employee_logs', ['employee_id'], unique=False)
        op.create_index(op.f('ix_employee_logs_timestamp'), 'employee_logs', ['timestamp'], unique=False)

    # Employees FK columns
    if _has_table(bind, 'employees'):
        if not _has_column(bind, 'employees', 'department_id'):
            op.add_column('employees', sa.Column('department_id', sa.Integer(), nullable=True))
            op.create_index(op.f('ix_employees_department_id'), 'employees', ['department_id'], unique=False)
            op.create_foreign_key('fk_employees_department_id', 'employees', 'departments', ['department_id'], ['id'], ondelete='SET NULL')
        if not _has_column(bind, 'employees', 'position_id'):
            op.add_column('employees', sa.Column('position_id', sa.Integer(), nullable=True))
            op.create_index(op.f('ix_employees_position_id'), 'employees', ['position_id'], unique=False)
            op.create_foreign_key('fk_employees_position_id', 'employees', 'positions', ['position_id'], ['id'], ondelete='SET NULL')
        # Legacy columns (if still present) set nullable for transition
        for legacy_col in ['department', 'position']:
            if _has_column(bind, 'employees', legacy_col):
                try:
                    op.alter_column('employees', legacy_col, nullable=True)
                except Exception:
                    pass


def downgrade():
    # Drop FK constraints and columns from employees
    op.drop_constraint('fk_employees_position_id', 'employees', type_='foreignkey')
    op.drop_constraint('fk_employees_department_id', 'employees', type_='foreignkey')
    op.drop_index(op.f('ix_employees_position_id'), table_name='employees')
    op.drop_index(op.f('ix_employees_department_id'), table_name='employees')
    op.drop_column('employees', 'position_id')
    op.drop_column('employees', 'department_id')

    # Restore department and position columns to NOT NULL
    op.alter_column('employees', 'department', nullable=False)
    op.alter_column('employees', 'position', nullable=False)

    # Drop employee_logs table
    op.drop_index(op.f('ix_employee_logs_timestamp'), table_name='employee_logs')
    op.drop_index(op.f('ix_employee_logs_employee_id'), table_name='employee_logs')
    op.drop_index(op.f('ix_employee_logs_id'), table_name='employee_logs')
    op.drop_table('employee_logs')

    # Drop positions table
    op.drop_index(op.f('ix_positions_name'), table_name='positions')
    op.drop_index(op.f('ix_positions_id'), table_name='positions')
    op.drop_table('positions')

    # Drop departments table
    op.drop_index(op.f('ix_departments_name'), table_name='departments')
    op.drop_index(op.f('ix_departments_id'), table_name='departments')
    op.drop_table('departments')
