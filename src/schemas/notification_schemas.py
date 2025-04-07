from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    customer_id: UUID
    timestamp: datetime
    message: str

    class Config:
        extra = "forbid"
