from datetime import datetime
from json import dumps
from random import choices
from random import randint
from random import uniform
from string import ascii_letters
from string import digits
from string import punctuation
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID
from uuid import uuid4

from src.db.models import Notification
from src.schemas.kafka_schemas import OrderStatus

EXPECTED_NOTIFICATION_RESPONSE_FIELDS = {
    "customer_id",
    "timestamp",
    "message",
}


def gen_str(
    length: int = 10,
    *,
    use_letters: bool = True,
    use_digits: bool = True,
    use_punctuation: bool = True,
) -> str:
    symbols = ""
    if use_letters:
        symbols += ascii_letters
    if use_digits:
        symbols += digits
    if use_punctuation:
        symbols += punctuation
    return "".join(choices(symbols, k=length))


def gen_headers(
    *, customer_id: UUID | None = None, is_admin: bool = False
) -> dict[str, str]:
    return {
        "x-customer-id": str(customer_id or uuid4()),
        "x-is-admin": str(is_admin).lower(),
    }


def generate_random_db_notification(customer_id: UUID | None = None) -> Notification:
    return Notification(
        id=randint(1, 99999),
        customer_id=customer_id or uuid4(),
        order_id=uuid4(),
        timestamp=datetime.now(),
        message=gen_str(50),
    )


def validate_notification_response(
    response_notification: dict[str, Any], expected_notification: Notification
) -> None:
    assert len(response_notification.keys()) == len(
        EXPECTED_NOTIFICATION_RESPONSE_FIELDS
    )
    assert set(response_notification.keys()) == EXPECTED_NOTIFICATION_RESPONSE_FIELDS
    for field in EXPECTED_NOTIFICATION_RESPONSE_FIELDS:
        expected_value = getattr(expected_notification, field)
        if isinstance(expected_value, datetime):
            expected_value = expected_value.isoformat()
        if isinstance(expected_value, UUID):
            expected_value = str(expected_value)
        assert response_notification[field] == expected_value, (
            f"{response_notification[field]} != {expected_value}"
        )


def generate_random_order_item() -> dict[str, str | int | float]:
    quantity = randint(1, 100)
    unit_price = round(uniform(10, 1000), 2)
    return {
        "product_id": str(uuid4()),
        "quantity": quantity,
        "unit_price": unit_price,
        "total_price": quantity * unit_price,
    }


def generate_random_order_event(
    status: OrderStatus,
) -> dict[str, str | list[dict[str, str | int | float]] | float]:
    item = generate_random_order_item()
    return {
        "customer_id": str(uuid4()),
        "order_id": str(uuid4()),
        "items": [item],
        "total_price": item["total_price"],
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "message": gen_str(50),
    }


def build_mock_msg(event: dict[str, Any]) -> MagicMock:
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.topic.return_value = "orders"
    mock_msg.partition.return_value = 0
    mock_msg.offset.return_value = randint(1, 99999)
    mock_msg.key.return_value = event["customer_id"]
    mock_msg.value.return_value = dumps(event).encode("utf-8")
    return mock_msg
