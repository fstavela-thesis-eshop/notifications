import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.helpers import HeaderNoSchema
from db.models import Notification
from db.session import get_db
from schemas.notification_schemas import NotificationResponse

logger = logging.getLogger(__name__)


notifications_router = APIRouter()


@notifications_router.get("", response_model=list[NotificationResponse])
def get_notifications(
    x_customer_id: Annotated[str, HeaderNoSchema()],
    x_is_admin: Annotated[bool, HeaderNoSchema()],
    db: Annotated[Session, Depends(get_db)],
) -> list[Notification]:
    if x_is_admin:
        return list(db.scalars(select(Notification)).all())
    query = select(Notification).where(Notification.customer_id == x_customer_id)
    return list(db.scalars(query).all())


@notifications_router.get(
    "/{customer_id}",
    response_model=list[NotificationResponse],
    responses={status.HTTP_403_FORBIDDEN: {}},
)
def get_notifications_for_customer(
    customer_id: UUID,
    x_customer_id: Annotated[str, HeaderNoSchema()],
    x_is_admin: Annotated[bool, HeaderNoSchema()],
    db: Annotated[Session, Depends(get_db)],
) -> list[Notification]:
    if str(customer_id) != x_customer_id and not x_is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't get notifications for other customers",
        )

    query = select(Notification).where(Notification.customer_id == x_customer_id)
    return list(db.scalars(query).all())
