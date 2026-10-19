from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

TransactionStatus = Literal["PENDING", "PROCESSING", "PROCESSED"]

PENDING: TransactionStatus = "PENDING"
PROCESSING: TransactionStatus = "PROCESSING"
PROCESSED: TransactionStatus = "PROCESSED"


def _as_utc_z(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class WebhookIn(BaseModel):
    transaction_id: str = Field(min_length=1)
    source_account: str = Field(min_length=1)
    destination_account: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = Field(min_length=1)


class WebhookAck(BaseModel):
    transaction_id: str


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str
    status: TransactionStatus
    created_at: datetime
    processed_at: datetime | None = None

    @field_serializer("created_at", "processed_at")
    def serialize_timestamp(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return _as_utc_z(value)


class HealthOut(BaseModel):
    status: str
    current_time: str
