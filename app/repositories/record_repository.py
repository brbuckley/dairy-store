from datetime import datetime
from itertools import count

from app.domain.record_port import RecordPort
from app.schemas.consumption_record import ConsumptionRecord


class RecordRepository(RecordPort):
    def __init__(self):
        # In-memory "database"
        self._db: list[ConsumptionRecord] = [
            ConsumptionRecord(
                id=1,
                batch_id=1,
                consumed_at=datetime.now(),
                order_id="ORDER-20251204-1234",
                qty=1000.0,
            ),
            ConsumptionRecord(
                id=2,
                batch_id=2,
                consumed_at=datetime.now(),
                order_id="ORDER-20251204-1234",
                qty=1000.0,
            ),
        ]
        self._id_seq = count(3)

    def insert(self, record: ConsumptionRecord):
        new_record = ConsumptionRecord(
            id=next(self._id_seq), **record.model_dump(exclude={"id"})
        )
        self._db.append(new_record)

    def list_all(self) -> list[ConsumptionRecord]:
        return self._db
