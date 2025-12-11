import time
from datetime import UTC, datetime, timedelta

from app.domain.batch_port import BatchPort, ConcurrencyError
from app.domain.record_port import RecordPort
from app.schemas.batches_schema import Batch
from app.schemas.consumption_record import ConsumptionRecord


class ResourceNotFoundError(Exception):
    pass


retries = 3
backoff = 0.25


class BatchService:
    def __init__(self, batch_port: BatchPort, record_port: RecordPort) -> None:
        self._batch_port = batch_port
        self._record_port = record_port

    def create(self, batch: Batch) -> Batch:
        return self._batch_port.upsert(batch)

    def list_all(self) -> list[Batch]:
        return self._batch_port.list_all_available()

    def read_by_id(self, batch_id: int) -> Batch:
        batch = self._batch_port.read_by_id(batch_id)
        if not batch:
            raise ResourceNotFoundError()
        return batch

    def consume(
        self, batch_id: int, qty: float, order_id: str | None
    ) -> Batch:
        now = datetime.now(UTC)
        for i in range(retries):
            batch = self.read_by_id(batch_id)
            new_volume = batch.volume_liters - qty
            if new_volume < 0:
                raise ValueError("Cannot consume more than available volume")
            batch.volume_liters = new_volume
            try:
                updated_batch = self._batch_port.upsert(batch)
                self._record_port.insert(
                    ConsumptionRecord(
                        batch_id=updated_batch.id,
                        consumed_at=now,
                        order_id=order_id,
                        qty=qty,
                    )
                )
                return updated_batch
            except ConcurrencyError:
                time.sleep(i * backoff)
        raise ConcurrencyError()

    def list_near_expiry(self, n_days: int) -> list[Batch]:
        now = datetime.now(UTC)
        return self._batch_port.list_all_between_dates(
            now, now + timedelta(days=n_days)
        )

    def delete(self, batch_id: int) -> None:
        self._batch_port.soft_delete(batch_id)
