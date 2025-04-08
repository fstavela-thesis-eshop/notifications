import logging
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockerFixture
from sqlalchemy import Select
from sqlalchemy import select

from src.db.models import Notification
from tests.helpers import gen_headers
from tests.helpers import generate_random_db_notification
from tests.helpers import validate_notification_response

logger = logging.getLogger(__name__)


def test_get_notifications_as_admin(
    api_client: TestClient, mock_db: MagicMock, mocker: MockerFixture
) -> None:
    customer_id = uuid4()
    mock_notification1 = generate_random_db_notification(customer_id=customer_id)
    mock_notification2 = generate_random_db_notification()

    mock_return = mocker.Mock()

    def _scalars(query: Select[Notification]) -> mocker.Mock:
        assert str(query.compile()) == str(select(Notification).compile())
        return mock_return

    mock_db.scalars = _scalars
    mock_return.all.return_value = [mock_notification1, mock_notification2]

    response = api_client.get(
        "/notifications",
        headers=gen_headers(customer_id=customer_id, is_admin=True),
    )

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)

    assert len(response_json) == 2
    validate_notification_response(response_json[0], mock_notification1)
    validate_notification_response(response_json[1], mock_notification2)


def test_get_notifications_as_non_admin(
    api_client: TestClient, mock_db: MagicMock, mocker: MockerFixture
) -> None:
    customer_id = uuid4()
    mock_notification1 = generate_random_db_notification(customer_id=customer_id)

    mock_return = mocker.Mock()

    def _scalars(query: Select[Notification]) -> mocker.Mock:
        assert str(query.compile()) == str(
            select(Notification).where(Notification.customer_id == customer_id)
        )
        return mock_return

    mock_db.scalars = _scalars
    mock_return.all.return_value = [mock_notification1]

    response = api_client.get(
        "/notifications",
        headers=gen_headers(customer_id=customer_id, is_admin=False),
    )

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)

    assert len(response_json) == 1
    validate_notification_response(response_json[0], mock_notification1)


def test_get_notifications_empty(
    api_client: TestClient, mock_db: MagicMock, mocker: MockerFixture
) -> None:
    mock_return = mocker.Mock()

    def _scalars(query: Select[Notification]) -> mocker.Mock:
        assert str(query.compile()) == str(select(Notification).compile())
        return mock_return

    mock_db.scalars = _scalars
    mock_return.all.return_value = []

    response = api_client.get(
        "/notifications",
        headers=gen_headers(is_admin=True),
    )

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 0


@pytest.mark.parametrize("customer_id", ("str", "123", str(uuid4()) + "a"))
@pytest.mark.parametrize("is_admin", (True, False))
def test_get_notifications_by_customer_id_wrong_id(
    api_client: TestClient, customer_id: str, is_admin: bool
) -> None:
    response = api_client.get(
        f"/notifications/{customer_id}",
        headers=gen_headers(is_admin=is_admin),
    )
    assert response.status_code == 422


def test_get_notifications_by_customer_id_different_id_as_non_admin(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        f"/notifications/{str(uuid4())}",
        headers=gen_headers(is_admin=False),
    )
    assert response.status_code == 403


def test_get_notifications_by_customer_id_different_id_as_admin(
    api_client: TestClient, mock_db: MagicMock, mocker: MockerFixture
) -> None:
    customer_id = uuid4()
    mock_notification1 = generate_random_db_notification(customer_id=customer_id)

    mock_return = mocker.Mock()

    def _scalars(query: Select[Notification]) -> mocker.Mock:
        assert str(query.compile()) == str(
            select(Notification).where(Notification.customer_id == customer_id)
        )
        return mock_return

    mock_db.scalars = _scalars
    mock_return.all.return_value = [mock_notification1]

    response = api_client.get(
        f"/notifications/{customer_id}",
        headers=gen_headers(is_admin=True),
    )

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)

    assert len(response_json) == 1
    validate_notification_response(response_json[0], mock_notification1)


@pytest.mark.parametrize("is_admin", (True, False))
def test_get_notifications_by_customer_id_correct(
    api_client: TestClient, mock_db: MagicMock, mocker: MockerFixture, is_admin: bool
) -> None:
    customer_id = uuid4()
    mock_notification1 = generate_random_db_notification(customer_id=customer_id)

    mock_return = mocker.Mock()

    def _scalars(query: Select[Notification]) -> mocker.Mock:
        assert str(query.compile()) == str(
            select(Notification).where(Notification.customer_id == customer_id)
        )
        return mock_return

    mock_db.scalars = _scalars
    mock_return.all.return_value = [mock_notification1]

    response = api_client.get(
        f"/notifications/{customer_id}",
        headers=gen_headers(customer_id=customer_id, is_admin=is_admin),
    )

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)

    assert len(response_json) == 1
    validate_notification_response(response_json[0], mock_notification1)
