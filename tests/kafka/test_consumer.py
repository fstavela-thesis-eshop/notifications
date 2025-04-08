from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.db.models import Notification
from src.kafka.consumer import consume
from src.schemas.kafka_schemas import OrderStatus
from tests.helpers import build_mock_msg
from tests.helpers import generate_random_order_event


@pytest.mark.parametrize(
    "status, message",
    [
        (OrderStatus.CREATED, "Order {} was successfully created."),
        (OrderStatus.PAID, "Order {} was paid. Thank you!"),
        (
            OrderStatus.SENT,
            "Items from order {} were shipped. Expect the arrival in the next 3 days.",
        ),
        (OrderStatus.DELIVERED, "Order {} was delivered."),
        (OrderStatus.CANCELLED, "Order {} was cancelled."),
    ],
)
def test_consume_event(
    mock_db: MagicMock, mocker: MockerFixture, status: OrderStatus, message: str
) -> None:
    event = generate_random_order_event(status)

    mock_consumer = MagicMock()
    mock_consumer.poll.side_effect = [build_mock_msg(event), None, KeyboardInterrupt()]
    mocker.patch("src.kafka.consumer.Consumer", return_value=mock_consumer)

    mocker.patch("src.kafka.consumer.get_db", return_value=iter([mock_db]))

    def _add_notification(notification: Notification) -> None:
        assert str(notification.customer_id) == event["customer_id"]
        assert str(notification.order_id) == event["order_id"]
        assert notification.message == message.format(event["order_id"])

    mock_db.add = _add_notification

    with pytest.raises(KeyboardInterrupt):
        consume()

    mock_db.commit.assert_called_once()
