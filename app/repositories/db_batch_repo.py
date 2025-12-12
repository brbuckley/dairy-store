from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select

from app.domain.batch_port import BatchPort, ConcurrencyError
from app.repositories.db.models import Batch as BatchModel
from app.repositories.db.session import SessionLocal
from app.schemas.batches_schema import Batch as BatchSchema


def model_to_schema(model_batch: BatchModel) -> BatchSchema:
    """Map an ORM Batch row to the Pydantic Batch schema and set private attrs."""
    data = {
        "id": model_batch.id,
        "batch_code": model_batch.batch_code,
        "received_at": model_batch.received_at,
        "shelf_life_days": model_batch.shelf_life_days,
        "volume_liters": model_batch.volume_liters,
        "fat_percent": model_batch.fat_percent,
    }
    schema = BatchSchema.model_validate(data)  # Pydantic v2

    # Set private attrs on the Pydantic instance (is_deleted / version)
    object.__setattr__(
        schema, "_is_deleted", bool(getattr(model_batch, "is_deleted", False))
    )
    object.__setattr__(
        schema, "_version", int(getattr(model_batch, "version", 0) or 0)
    )
    object.__setattr__(schema, "_expiry", model_batch.expiry)

    return schema


def schema_to_model(batch_schema: BatchSchema) -> BatchModel:
    """Return kwargs suitable for constructing/updating the ORM Batch from a Pydantic Batch."""
    # Exclude private attrs and None id (id handled by DB on insert)
    batch_dict = batch_schema.model_dump(
        exclude={"_is_deleted", "_version"}, exclude_none=True
    )
    batch_dict["is_deleted"] = batch_schema._is_deleted
    batch_dict["version"] = batch_schema._version
    batch_dict["expiry"] = batch_schema._expiry
    # model_dump produces keys matching column names (id, batch_code, ...)
    return BatchModel(**{k: v for k, v in batch_dict.items() if k != "id"})


class DBBatchRepository(BatchPort):
    """
    SQLAlchemy-backed repository implementing the BatchPort interface.
    Uses SessionLocal from app.repositories.db.session.
    """

    def __init__(self) -> None:
        # No global state here; sessions are created per-operation
        pass

    def upsert(self, batch_schema: BatchSchema) -> BatchSchema:
        """
        Insert or update a Batch.
        - If batch.id is None -> create new row
        - If batch.id is present -> update existing row (partial update)
          If batch.version is provided the update requires equality with stored version,
          otherwise it applies unconditional update.
        Returns the fresh Pydantic BatchSchema (with new version set).
        """

        with SessionLocal() as session:
            if batch_schema.id:
                stmt = select(BatchModel).where(
                    BatchModel.id == batch_schema.id
                )
                old_batch = session.execute(stmt).scalars().one_or_none()
                if old_batch.version > batch_schema._version:
                    raise ConcurrencyError()
                new_batch = batch_schema.model_dump(
                    exclude_unset=True, exclude_none=True
                )
                new_batch["version"] = batch_schema._version + 1
                for field, value in new_batch.items():
                    setattr(old_batch, field, value)
                session.add(old_batch)
                session.commit()
                session.refresh(old_batch)
                return model_to_schema(old_batch)
            new_batch = schema_to_model(batch_schema)
            session.add(new_batch)
            session.commit()
            session.refresh(new_batch)
            return model_to_schema(new_batch)

    def list_all_available(self) -> list[BatchSchema]:
        """
        Return list of available batches:
         - volume_liters > 0
         - not deleted
         - not expired (uses received_at + shelf_life_days < now to detect expiry)
        """

        with SessionLocal() as session:
            stmt = select(BatchModel).where(
                BatchModel.is_deleted == False,
                BatchModel.volume_liters > 0,
                func.now() < BatchModel.expiry,
            )
            return [
                model_to_schema(batch)
                for batch in session.execute(stmt).scalars().all()
            ]

    def list_all_between_dates(
        self, min_date: datetime, max_date: datetime
    ) -> list[BatchSchema]:
        """
        Return batches whose expiry is between min_date and max_date (inclusive).
        For portability we read candidates from DB and compute expiry in Python.
        """
        with SessionLocal() as session:
            stmt = select(BatchModel).where(
                BatchModel.is_deleted == False,
                BatchModel.volume_liters > 0,
                func.now() < BatchModel.expiry,
                BatchModel.expiry >= min_date,
                BatchModel.expiry <= max_date,
            )
            return [
                model_to_schema(batch)
                for batch in session.execute(stmt).scalars().all()
            ]

    def read_by_id(self, batch_id: int) -> BatchSchema | None:
        """
        Return the batch if it exists, has volume, is not expired and not deleted.
        Returns None if not found / not available.
        """
        with SessionLocal() as session:
            stmt = select(BatchModel).where(
                BatchModel.id == batch_id,
                BatchModel.is_deleted == False,
                BatchModel.volume_liters > 0,
                func.now() < BatchModel.expiry,
            )
            return model_to_schema(
                session.execute(stmt).scalars().one_or_none()
            )

    def soft_delete(self, batch_id: int) -> None:
        with SessionLocal() as session:
            stmt = select(BatchModel).where(BatchModel.id == batch_id)
            batch = session.execute(stmt).scalars().one_or_none()
            batch.is_deleted = True
            session.add(batch)
            session.commit()

    def list_all(self) -> list[BatchSchema]:
        """Return all batches (including deleted)."""
        with SessionLocal() as session:
            return [
                model_to_schema(batch)
                for batch in session.execute(select(BatchModel))
                .scalars()
                .all()
            ]
