from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    SENT = "sent"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float
    total_price: float

    model_config = ConfigDict(extra="forbid")


class OrderEvent(BaseModel):
    customer_id: UUID
    order_id: UUID
    items: list[OrderItem]
    total_price: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    message: str

    model_config = ConfigDict(extra="forbid")
