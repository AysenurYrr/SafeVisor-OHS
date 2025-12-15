"""Add ondelete to employee foreign keys

Revision ID: 98272b89702e
Revises: 52a6eeb34476
Create Date: 2025-12-15 19:45:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98272b89702e'
down_revision = '52a6eeb34476'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ondelete='SET NULL' to employee_id foreign keys in violations and pose_alerts tables.
    
    This allows employees to be deleted even when they have related violations or pose_alerts.
    The employee_id will be set to NULL in those records when the employee is deleted.
    """
    # For PostgreSQL, we need to drop and recreate the foreign key constraints
    # with the ondelete clause
    
    # Update violations table
    with op.batch_alter_table('violations', schema=None) as batch_op:
        # Drop existing foreign key constraint
        batch_op.drop_constraint('violations_employee_id_fkey', type_='foreignkey')
        # Re-create with ondelete='SET NULL'
        batch_op.create_foreign_key(
            'violations_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id'],
            ondelete='SET NULL'
        )
    
    # Update pose_alerts table
    with op.batch_alter_table('pose_alerts', schema=None) as batch_op:
        # Drop existing foreign key constraint
        batch_op.drop_constraint('pose_alerts_employee_id_fkey', type_='foreignkey')
        # Re-create with ondelete='SET NULL'
        batch_op.create_foreign_key(
            'pose_alerts_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id'],
            ondelete='SET NULL'
        )


def downgrade() -> None:
    """Revert the foreign key constraints to their original state without ondelete."""
    
    # Revert violations table
    with op.batch_alter_table('violations', schema=None) as batch_op:
        # Drop the foreign key with ondelete
        batch_op.drop_constraint('violations_employee_id_fkey', type_='foreignkey')
        # Re-create without ondelete clause
        batch_op.create_foreign_key(
            'violations_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id']
        )
    
    # Revert pose_alerts table
    with op.batch_alter_table('pose_alerts', schema=None) as batch_op:
        # Drop the foreign key with ondelete
        batch_op.drop_constraint('pose_alerts_employee_id_fkey', type_='foreignkey')
        # Re-create without ondelete clause
        batch_op.create_foreign_key(
            'pose_alerts_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id']
        )
