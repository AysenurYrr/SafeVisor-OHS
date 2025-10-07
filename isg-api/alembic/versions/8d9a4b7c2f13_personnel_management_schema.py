"""normalize personnel management schema (conditional)

Revision ID: 8d9a4b7c2f13
Revises: 20251007_170831
Create Date: 2025-10-07 18:05:00

This migration re-applies (idempotently) the personnel management structures
in case an earlier migration with non-standard revision id was not executed.

Operations are guarded by introspection so it is safe to run on databases
where the schema already exists.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

revision = '8d9a4b7c2f13'
down_revision = '20251007_170831'
branch_labels = None
depends_on = None


def _has_table(bind, name: str) -> bool:
    insp = inspect(bind)
    return name in insp.get_table_names()


def _has_column(bind, table: str, column: str) -> bool:
    insp = inspect(bind)
    try:
        return column in [c['name'] for c in insp.get_columns(table)]
    except Exception:
        return False


def upgrade():
    bind = op.get_bind()

    # Create departments table if missing
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
        op.create_index('ix_departments_id', 'departments', ['id'])
        op.create_index('ix_departments_name', 'departments', ['name'], unique=True)

    # Create positions table if missing
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
        op.create_index('ix_positions_id', 'positions', ['id'])
        op.create_index('ix_positions_name', 'positions', ['name'])

    # Create employee_logs table if missing
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
        op.create_index('ix_employee_logs_id', 'employee_logs', ['id'])
        op.create_index('ix_employee_logs_employee_id', 'employee_logs', ['employee_id'])
        op.create_index('ix_employee_logs_timestamp', 'employee_logs', ['timestamp'])

    # Ensure employees table exists before altering
    if _has_table(bind, 'employees'):
        # Add department_id if missing
        if not _has_column(bind, 'employees', 'department_id'):
            op.add_column('employees', sa.Column('department_id', sa.Integer(), nullable=True))
            op.create_index('ix_employees_department_id', 'employees', ['department_id'])
            op.create_foreign_key('fk_employees_department_id', 'employees', 'departments', ['department_id'], ['id'], ondelete='SET NULL')
        # Add position_id if missing
        if not _has_column(bind, 'employees', 'position_id'):
            op.add_column('employees', sa.Column('position_id', sa.Integer(), nullable=True))
            op.create_index('ix_employees_position_id', 'employees', ['position_id'])
            op.create_foreign_key('fk_employees_position_id', 'employees', 'positions', ['position_id'], ['id'], ondelete='SET NULL')
        # Make legacy department/position nullable (ignore if already nullable)
        try:
            op.alter_column('employees', 'department', existing_type=sa.String(length=100), nullable=True)
        except Exception:
            pass
        try:
            op.alter_column('employees', 'position', existing_type=sa.String(length=100), nullable=True)
        except Exception:
            pass


def downgrade():
    bind = op.get_bind()
    # Drop added FKs/columns conditionally (safe for partial states)
    if _has_table(bind, 'employees'):
        if _has_column(bind, 'employees', 'position_id'):
            try:
                op.drop_constraint('fk_employees_position_id', 'employees', type_='foreignkey')
            except Exception:
                pass
            try:
                op.drop_index('ix_employees_position_id', table_name='employees')
            except Exception:
                pass
            try:
                op.drop_column('employees', 'position_id')
            except Exception:
                pass
        if _has_column(bind, 'employees', 'department_id'):
            try:
                op.drop_constraint('fk_employees_department_id', 'employees', type_='foreignkey')
            except Exception:
                pass
            try:
                op.drop_index('ix_employees_department_id', table_name='employees')
            except Exception:
                pass
            try:
                op.drop_column('employees', 'department_id')
            except Exception:
                pass
    # Drop tables only if they exist (reverse order to satisfy FKs)
    if _has_table(bind, 'employee_logs'):
        try:
            op.drop_index('ix_employee_logs_timestamp', table_name='employee_logs')
            op.drop_index('ix_employee_logs_employee_id', table_name='employee_logs')
            op.drop_index('ix_employee_logs_id', table_name='employee_logs')
        except Exception:
            pass
        op.drop_table('employee_logs')
    if _has_table(bind, 'positions'):
        try:
            op.drop_index('ix_positions_name', table_name='positions')
            op.drop_index('ix_positions_id', table_name='positions')
        except Exception:
            pass
        op.drop_table('positions')
    if _has_table(bind, 'departments'):
        try:
            op.drop_index('ix_departments_name', table_name='departments')
            op.drop_index('ix_departments_id', table_name='departments')
        except Exception:
            pass
        op.drop_table('departments')
