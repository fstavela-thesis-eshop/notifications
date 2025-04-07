import logging
from os import getenv

from confluent_kafka import Consumer

from db.models import Notification
from db.session import get_db
from schemas.kafka_schemas import OrderEvent
from schemas.kafka_schemas import OrderStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ORDERS_TOPIC = getenv("KAFKA_ORDERS_TOPIC", "orders")

consumer_conf = {
    "bootstrap.servers": getenv("KAFKA_SERVER", "localhost:9092"),
    "group.id": "notifications_group",
}


def consume() -> None:
    consumer = Consumer(consumer_conf)
    consumer.subscribe([ORDERS_TOPIC])
    logger.info(f"Consumer subscribed to '{ORDERS_TOPIC}'")

    db = next(get_db())

    while True:
        try:
            msg = consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue

            logger.info(
                f"Kafka event consumed:\nTopic: {msg.topic()}; "
                f"Partition: {msg.partition()}; Offset: {msg.offset()}\n"
                f"Key: {msg.key()}; Message: {msg.value()}"
            )

            order_event = OrderEvent.model_validate_json(msg.value().decode("utf-8"))

            if order_event.status == OrderStatus.CREATED:
                notification_message = (
                    f"Order {order_event.order_id} was successfully created."
                )
            elif order_event.status == OrderStatus.PAID:
                notification_message = (
                    f"Order {order_event.order_id} was paid. Thank you!"
                )
            elif order_event.status == OrderStatus.SENT:
                notification_message = (
                    f"Items from order {order_event.order_id} were shipped. "
                    f"Expect the arrival in the next 3 days."
                )
            elif order_event.status == OrderStatus.DELIVERED:
                notification_message = f"Order {order_event.order_id} was delivered."
            elif order_event.status == OrderStatus.CANCELLED:
                notification_message = f"Order {order_event.order_id} was cancelled."
            else:
                logger.error(f"Unknown order status: {order_event.status}")
                continue

            db_notification = Notification(
                customer_id=order_event.customer_id,
                order_id=order_event.order_id,
                message=notification_message,
            )

            db.add(db_notification)
            db.commit()
        except Exception as err:
            logger.error(f"Error when consuming kafka events: {err}")


if __name__ == "__main__":
    consume()
