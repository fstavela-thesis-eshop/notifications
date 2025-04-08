from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class NotificationResponse(BaseModel):
    customer_id: UUID
    timestamp: datetime
    message: str

    model_config = ConfigDict(extra="forbid")
