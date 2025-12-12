from datetime import datetime, timedelta
from itertools import count

from app.domain.batch_port import BatchPort, ConcurrencyError
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
            batch.update_version()
            for i, old_batch in enumerate(self._db):
                if old_batch.id == batch.id:
                    # Only update fields provided by the caller
                    partial_update = batch.model_dump(
                        exclude_unset=True, exclude_none=True
                    )
                    if old_batch._version >= batch._version:
                        raise ConcurrencyError()
                    new_batch = old_batch.model_copy(update=partial_update)
                    new_batch.update_version()
                    self._db[i] = new_batch
                    return new_batch
        new_batch = Batch(
            id=next(self._id_seq), **batch.model_dump(exclude={"id"})
        )
        self._db.append(new_batch)
        return new_batch.model_copy()

    def list_all_available(self) -> list[Batch]:
        return [
            batch.model_copy()
            for batch in self._db
            if batch.volume_liters > 0
            and not batch.is_expired()
            and not batch._is_deleted
        ]

    def list_all_between_dates(
        self, min_date: datetime, max_date: datetime
    ) -> list[Batch]:
        return [
            batch.model_copy()
            for batch in self._db
            if min_date
            <= batch.received_at + timedelta(days=batch.shelf_life_days)
            <= max_date
            and not batch.is_expired()
            and not batch._is_deleted
        ]

    def read_by_id(self, batch_id: int) -> Batch | None:
        for batch in self._db:
            if (
                batch.id == batch_id
                and batch.volume_liters > 0
                and not batch.is_expired()
                and not batch._is_deleted
            ):
                return batch.model_copy()
        return None

    def soft_delete(self, batch_id: int) -> None:
        for batch in self._db:
            if batch.id == batch_id:
                batch._is_deleted = True

    def list_all(self) -> list[Batch]:
        return self._db
