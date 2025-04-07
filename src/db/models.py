from datetime import UTC
from datetime import datetime

from sqlalchemy import UUID
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _time_now() -> datetime:
    return datetime.now(UTC)


class Notification(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "notifications"

    id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    order_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=_time_now)
    message = Column(String(1024), nullable=False)
