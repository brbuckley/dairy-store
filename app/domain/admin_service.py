from app.domain.batch_port import BatchPort
from app.domain.record_port import RecordPort
from app.schemas.batches_schema import Batch
from app.schemas.consumption_record import ConsumptionRecord


class AdminService:
    def __init__(self, batch_port: BatchPort, record_port: RecordPort) -> None:
        self._batch_port = batch_port
        self._record_port = record_port

    def list_all_consumption_recors(self) -> list[ConsumptionRecord]:
        return self._record_port.list_all()

    def list_all_batches(self) -> list[Batch]:
        return self._batch_port.list_all()
