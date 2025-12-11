from datetime import datetime, timedelta
from itertools import count

from app.domain.batch_port import BatchPort
from app.schemas.batches_schema import Batch


class BatchRepository(BatchPort):
    def __init__(self):
        # In-memory "database"
        self._db: list[Batch] = [
            Batch(
                id=1,
                batch_code="SCH-20251204-0001",
                received_at=datetime.now(),
                shelf_life_days=7,
                volume_liters=1000.0,
                fat_percent=3.5,
            ),
            Batch(
                id=2,
                batch_code="SCH-20251204-0002",
                received_at=datetime.now(),
                shelf_life_days=14,
                volume_liters=2000.0,
                fat_percent=5.2,
            ),
        ]
        self._id_seq = count(3)  # simple auto-incrementing ID generator

    def upsert(self, batch: Batch) -> Batch:
        if batch.id:
            for i, saved in enumerate(self._db):
                if saved.id == batch.id:
                    # Only update fields provided by the caller
                    partial_update = batch.model_dump(
                        exclude_unset=True, exclude_none=True
                    )
                    updated = saved.model_copy(update=partial_update)
                    self._db[i] = updated
                    return updated
        new_batch = Batch(
            id=next(self._id_seq), **batch.model_dump(exclude={"id"})
        )
        self._db.append(new_batch)
        return new_batch

    def list_all(self) -> list[Batch]:
        return [
            b
            for b in self._db
            if b.volume_liters > 0 and not b.is_expired() and not b._is_deleted
        ]

    def list_all_between_dates(
        self, min_date: datetime, max_date: datetime
    ) -> list[Batch]:
        return [
            batch
            for batch in self._db
            if min_date
            <= batch.received_at + timedelta(days=batch.shelf_life_days)
            <= max_date
        ]

    def read_by_id(self, batch_id: int) -> Batch | None:
        for batch in self._db:
            if (
                batch.id == batch_id
                and batch.volume_liters > 0
                and not batch.is_expired()
                and not batch._is_deleted
            ):
                return batch
        return None

    def soft_delete(self, batch_id: int) -> None:
        for batch in self._db:
            if batch.id == batch_id:
                batch._is_deleted = True
