from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field, PrivateAttr, field_validator


class Batch(BaseModel):
    id: int | None = None
    batch_code: str = Field(
        ...,
        min_length=1,
        pattern=r"^[A-Z]{3}-\d{8}-\d{4}$",
    )
    received_at: datetime
    shelf_life_days: int = Field(
        default=7,
        ge=1,
        le=30,
    )
    volume_liters: float = Field(
        ...,
        ge=0,
    )
    fat_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    _is_deleted: bool = PrivateAttr(default=False)

    @field_validator("received_at")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        # If naive, assume UTC
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        # If offset-aware but not UTC, normalize to UTC
        return value.astimezone(UTC)

    def is_expired(self) -> bool:
        return self.received_at + timedelta(
            days=self.shelf_life_days
        ) < datetime.now(UTC)
