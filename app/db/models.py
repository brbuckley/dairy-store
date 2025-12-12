# app/db/models.py
from datetime import timedelta

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True)
    batch_code = Column(String(32), nullable=False, unique=True, index=True)
    received_at = Column(DateTime(timezone=True), nullable=False)
    shelf_life_days = Column(Integer, nullable=False)
    volume_liters = Column(Float, nullable=False)
    fat_percent = Column(Float, nullable=True)
    is_deleted = Column(Boolean, nullable=False)
    version = Column(Integer, nullable=False)
    expiry = Column(DateTime(timezone=True), nullable=False)

    # optional: consumption records backref
    consumption_records = relationship(
        "ConsumptionRecord",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class ConsumptionRecord(Base):
    __tablename__ = "consumption_records"

    id = Column(Integer, primary_key=True)
    batch_id = Column(
        Integer,
        ForeignKey("batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consumed_at = Column(DateTime(timezone=True), nullable=False)
    order_id = Column(String(64), nullable=True)
    qty = Column(Float, nullable=False)

    batch = relationship("Batch", back_populates="consumption_records")
