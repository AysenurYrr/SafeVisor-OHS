"""
Add uuid column to employees table, backfill values, enforce NOT NULL and unique.

This migration addresses runtime errors where the application expects an
`employees.uuid` column that doesn't exist in existing databases.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "20250922_000001_add_uuid_to_employees"
down_revision = None
branch_labels = None
depends_on = None


def _has_column(connection, table: str, column: str) -> bool:
    inspector = sa.inspect(connection)
    cols = [c["name"] for c in inspector.get_columns(table)]
    return column in cols


def _has_constraint(connection, table: str, name: str) -> bool:
    inspector = sa.inspect(connection)
    constraints = inspector.get_unique_constraints(table)
    return any(c.get("name") == name for c in constraints)


def upgrade() -> None:
    bind = op.get_bind()

    # Add the column if it doesn't exist
    if not _has_column(bind, "employees", "uuid"):
        op.add_column(
            "employees",
            sa.Column("uuid", sa.String(length=36), nullable=True),
        )

        # Backfill using Postgres uuid generator if available; fall back to random uuids in Python if needed
        try:
            # uuid-ossp extension function; cast to text to fit String(36)
            bind.execute(text("UPDATE employees SET uuid = uuid_generate_v4()::text WHERE uuid IS NULL"))
        except Exception:
            # Fallback: generate in application side (works on any DB)
            import uuid as _py_uuid
            result = bind.execute(text("SELECT id FROM employees WHERE uuid IS NULL"))
            rows = result.fetchall()
            for (emp_id,) in rows:
                bind.execute(
                    text("UPDATE employees SET uuid = :uuid WHERE id = :id"),
                    {"uuid": str(_py_uuid.uuid4()), "id": emp_id},
                )

        # Enforce NOT NULL
        op.alter_column(
            "employees",
            "uuid",
            existing_type=sa.String(length=36),
            nullable=False,
        )

    # Create unique constraint if missing
    if not _has_constraint(bind, "employees", "uq_employees_uuid"):
        op.create_unique_constraint("uq_employees_uuid", "employees", ["uuid"])


def downgrade() -> None:
    bind = op.get_bind()
    # Drop unique constraint if present
    if _has_constraint(bind, "employees", "uq_employees_uuid"):
        op.drop_constraint("uq_employees_uuid", "employees", type_="unique")

    # Drop column if present
    if _has_column(bind, "employees", "uuid"):
        op.drop_column("employees", "uuid")
