from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class ConsumptionRecord(BaseModel):
    id: int | None = None
    batch_id: int
    consumed_at: datetime
    order_id: str | None = Field(pattern=r"^[A-Z]{5}-\d{8}-\d{4}$")
    qty: float = Field(
        ...,
        ge=0,
    )

    @field_validator("consumed_at")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        # If naive, assume UTC
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        # If offset-aware but not UTC, normalize to UTC
        return value.astimezone(UTC)
