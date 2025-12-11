from typing import Protocol

from app.schemas.consumption_record import ConsumptionRecord


class RecordPort(Protocol):
    def insert(self, record: ConsumptionRecord) -> None:
        pass

    def list_all(self) -> list[ConsumptionRecord]:
        pass
