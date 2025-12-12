"""seed initial batches

Revision ID: 9da85c0c28d9
Revises: 3b3b7932d5a1
Create Date: 2025-12-12 01:21:56.990707

"""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9da85c0c28d9"
down_revision: str | Sequence[str] | None = "3b3b7932d5a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    batches_table = sa.table(
        "batches",
        sa.column("id", sa.Integer),
        sa.column("batch_code", sa.String),
        sa.column("received_at", sa.DateTime(timezone=True)),
        sa.column("shelf_life_days", sa.Integer),
        sa.column("volume_liters", sa.Float),
        sa.column("fat_percent", sa.Float),
        sa.column("is_deleted", sa.Boolean),
        sa.column("version", sa.Integer),
        sa.column("expiry", sa.DateTime(timezone=True)),
    )

    now_utc = datetime.now(UTC)

    op.bulk_insert(
        batches_table,
        [
            {
                "id": 1,
                "batch_code": "SCH-20251204-0001",
                "received_at": now_utc,
                "shelf_life_days": 7,
                "volume_liters": 1000.0,
                "fat_percent": 3.5,
                "is_deleted": False,
                "version": 1,
                "expiry": now_utc + timedelta(days=7),
            },
            {
                "id": 2,
                "batch_code": "SCH-20251204-0002",
                "received_at": now_utc,
                "shelf_life_days": 14,
                "volume_liters": 2000.0,
                "fat_percent": 5.2,
                "is_deleted": False,
                "version": 1,
                "expiry": now_utc + timedelta(days=14),
            },
        ],
    )


def downgrade() -> None:
    # remove seeded rows by batch_code (safe + reversible)
    op.execute(
        sa.text("DELETE FROM batches WHERE batch_code IN (:b1, :b2)"),
        {"b1": "SCH-20251204-0001", "b2": "SCH-20251204-0002"},
    )
