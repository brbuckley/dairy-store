from __future__ import annotations

from sqlalchemy import select

from app.domain.record_port import RecordPort
from app.repositories.db.models import ConsumptionRecord as RecordModel
from app.repositories.db.session import SessionLocal
from app.schemas.consumption_record import ConsumptionRecord as RecordSchema


def model_to_schema(model_record: RecordModel) -> RecordSchema:
    """Map an ORM Record row to the Pydantic Batch schema and set private attrs."""
    data = {
        "id": model_record.id,
        "batch_id": model_record.batch_id,
        "consumed_at": model_record.consumed_at,
        "order_id": model_record.order_id,
        "qty": model_record.qty,
    }
    return RecordSchema.model_validate(data)  # Pydantic v2


def schema_to_model(record_schema: RecordSchema) -> RecordModel:
    batch_dict = record_schema.model_dump(exclude_none=True)
    return RecordModel(**{k: v for k, v in batch_dict.items() if k != "id"})


class DBRecordRepository(RecordPort):
    def __init__(self):
        pass

    def insert(self, record_schema: RecordSchema):
        with SessionLocal() as session:
            new_record = schema_to_model(record_schema)
            session.add(new_record)
            session.commit()
            session.refresh(new_record)
            return model_to_schema(new_record)

    def list_all(self) -> list[RecordSchema]:
        """Return all records."""
        with SessionLocal() as session:
            return [
                model_to_schema(record)
                for record in session.execute(select(RecordModel))
                .scalars()
                .all()
            ]
