"""Add ondelete to employee FKs in violations and pose_alerts

Revision ID: 74ac3d76478e
Revises: 52a6eeb34476
Create Date: 2025-12-15 20:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74ac3d76478e'
down_revision = '52a6eeb34476'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ON DELETE SET NULL to employee_id foreign keys in violations and pose_alerts tables.
    
    This allows employees to be deleted while preserving historical violation and pose alert records.
    The employee_id will be set to NULL when an employee is deleted.
    """
    # Use batch mode for better compatibility with different database backends
    with op.batch_alter_table('violations', schema=None) as batch_op:
        # Drop existing FK constraint
        batch_op.drop_constraint('violations_employee_id_fkey', type_='foreignkey')
        # Recreate with ON DELETE SET NULL
        batch_op.create_foreign_key(
            'violations_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id'],
            ondelete='SET NULL'
        )
    
    with op.batch_alter_table('pose_alerts', schema=None) as batch_op:
        # Drop existing FK constraint
        batch_op.drop_constraint('pose_alerts_employee_id_fkey', type_='foreignkey')
        # Recreate with ON DELETE SET NULL
        batch_op.create_foreign_key(
            'pose_alerts_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id'],
            ondelete='SET NULL'
        )


def downgrade() -> None:
    """Remove ON DELETE SET NULL from employee_id foreign keys."""
    with op.batch_alter_table('pose_alerts', schema=None) as batch_op:
        batch_op.drop_constraint('pose_alerts_employee_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'pose_alerts_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id']
        )
    
    with op.batch_alter_table('violations', schema=None) as batch_op:
        batch_op.drop_constraint('violations_employee_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'violations_employee_id_fkey',
            'employees',
            ['employee_id'],
            ['id']
        )
