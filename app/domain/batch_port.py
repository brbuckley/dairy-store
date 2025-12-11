# app/domain/batch_port.py

from abc import ABC, abstractmethod
from datetime import datetime

from app.schemas.batches_schema import Batch


class BatchPort(ABC):
    @abstractmethod
    def upsert(self, batch: Batch) -> Batch:
        pass

    @abstractmethod
    def list_all(self) -> list[Batch]:
        pass

    @abstractmethod
    def list_all_between_dates(
        self, min_date: datetime, max_date: datetime
    ) -> list[Batch]:
        pass

    @abstractmethod
    def read_by_id(self, batch_id: int) -> Batch | None:
        pass

    @abstractmethod
    def soft_delete(self, batch_id: int) -> None:
        pass
