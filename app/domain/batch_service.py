# app/domain/batch_service.py

from datetime import UTC, datetime, timedelta

from app.domain.batch_port import BatchPort
from app.schemas.batches_schema import Batch


class ResourceNotFound(Exception):
    pass


class BatchService:
    def __init__(self, port: BatchPort) -> None:
        self._port = port

    def create(self, batch: Batch) -> Batch:
        return self._port.upsert(batch)

    def list_all(self) -> list[Batch]:
        return self._port.list_all()

    def read_by_id(self, batch_id: int) -> Batch:
        batch = self._port.read_by_id(batch_id)
        if not batch:
            raise ResourceNotFound()
        return batch

    def consume(
        self, batch_id: int, qty: float, order_id: str | None
    ) -> Batch:
        batch = self.read_by_id(batch_id)
        new_volume = batch.volume_liters - qty
        if new_volume < 0:
            raise ValueError("Cannot consume more than available volume")
        batch.volume_liters = new_volume
        return self._port.upsert(batch)

    def list_near_expiry(self, n_days: int) -> list[Batch]:
        now = datetime.now(UTC)
        return self._port.list_all_between_dates(
            now, now + timedelta(days=n_days)
        )

    def delete(self, batch_id: int) -> None:
        self._port.soft_delete(batch_id)
