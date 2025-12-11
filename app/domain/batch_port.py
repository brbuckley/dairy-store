from datetime import datetime
from typing import Protocol

from app.schemas.batches_schema import Batch


class BatchPort(Protocol):
    def upsert(self, batch: Batch) -> Batch:
        pass

    def list_all(self) -> list[Batch]:
        pass

    def list_all_between_dates(
        self, min_date: datetime, max_date: datetime
    ) -> list[Batch]:
        pass

    def read_by_id(self, batch_id: int) -> Batch | None:
        pass

    def soft_delete(self, batch_id: int) -> None:
        pass
