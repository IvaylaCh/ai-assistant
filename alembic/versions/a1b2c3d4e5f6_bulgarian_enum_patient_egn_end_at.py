"""Bulgarian enum values, rename EGN to patient_egn, add end_at

Revision ID: a1b2c3d4e5f6
Revises: c3e50315d320
Create Date: 2026-03-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'c3e50315d320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename EGN → patient_egn
    op.alter_column('appointments', 'EGN', new_column_name='patient_egn')

    # 2. Add index on patient_egn
    op.create_index('ix_appointments_patient_egn', 'appointments', ['patient_egn'], unique=False)

    # 3. Add end_at column (nullable first so existing rows can be backfilled)
    op.add_column('appointments', sa.Column('end_at', sa.DateTime(), nullable=True))

    # 4. Backfill end_at = start_at + 20 minutes for existing rows
    op.execute("UPDATE appointments SET end_at = start_at + INTERVAL '20 minutes' WHERE end_at IS NULL")

    # 5. Set NOT NULL constraint on end_at
    op.alter_column('appointments', 'end_at', nullable=False)

    # 6. Change enum values English → Bulgarian.
    #    PostgreSQL forbids using ADD VALUE'd values in the same transaction,
    #    so we convert the column to VARCHAR first, update the data, then
    #    drop and recreate the enum type with Bulgarian values only.
    op.execute(
        "ALTER TABLE appointments "
        "ALTER COLUMN status TYPE VARCHAR(20) "
        "USING status::text"
    )
    op.execute("DROP TYPE appointmentstatus")

    op.execute("UPDATE appointments SET status = 'ЗАПИСАН'  WHERE status = 'BOOKED'")
    op.execute("UPDATE appointments SET status = 'ОТМЕНЕН'  WHERE status = 'CANCELLED'")
    op.execute("UPDATE appointments SET status = 'ЗАВЪРШЕН' WHERE status = 'COMPLETED'")

    op.execute("CREATE TYPE appointmentstatus AS ENUM ('ЗАПИСАН', 'ОТМЕНЕН', 'ЗАВЪРШЕН')")
    op.execute(
        "ALTER TABLE appointments "
        "ALTER COLUMN status TYPE appointmentstatus "
        "USING status::appointmentstatus"
    )


def downgrade() -> None:
    # Reverse enum to English
    op.execute("ALTER TYPE appointmentstatus RENAME TO appointmentstatus_old")
    op.execute("CREATE TYPE appointmentstatus AS ENUM ('BOOKED', 'CANCELLED', 'COMPLETED')")
    op.execute("UPDATE appointments SET status = 'BOOKED' WHERE status = 'ЗАПИСАН'")
    op.execute("UPDATE appointments SET status = 'CANCELLED' WHERE status = 'ОТМЕНЕН'")
    op.execute("UPDATE appointments SET status = 'COMPLETED' WHERE status = 'ЗАВЪРШЕН'")
    op.execute(
        "ALTER TABLE appointments "
        "ALTER COLUMN status TYPE appointmentstatus "
        "USING status::text::appointmentstatus"
    )
    op.execute("DROP TYPE appointmentstatus_old")

    # Remove end_at
    op.drop_column('appointments', 'end_at')

    # Remove patient_egn index and rename back
    op.drop_index('ix_appointments_patient_egn', table_name='appointments')
    op.alter_column('appointments', 'patient_egn', new_column_name='EGN')
