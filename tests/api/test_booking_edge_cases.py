"""Restful-Booker edge cases: health check, listing, filters, bad input and one documented defect."""
import pytest

from api.booker import BookerClient

pytestmark = pytest.mark.api


@pytest.fixture(scope="module")
def api():
    client = BookerClient()
    if client.s.get(f"{client.base}/ping", timeout=20).status_code != 201:
        pytest.skip("Restful-Booker is down")
    return client


def test_health_check_answers_201(api):
    assert api.s.get(f"{api.base}/ping", timeout=20).status_code == 201


def test_list_returns_booking_ids(api):
    response = api.list()
    assert response.status_code == 200
    ids = response.json()
    assert ids and all(isinstance(item["bookingid"], int) for item in ids)


def test_filter_by_unknown_name_returns_empty_list(api):
    response = api.list(firstname="Nobody-QA-Probe", lastname="Nowhere-QA-Probe")
    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_checkin_date_is_accepted(api):
    assert api.list(checkin="2014-01-01").status_code == 200


@pytest.mark.parametrize("booking_id", ["abc", "0", "999999999"])
def test_unknown_or_invalid_id_is_404(api, booking_id):
    assert api.get(booking_id).status_code == 404


def test_malformed_json_is_rejected_with_400(api):
    response = api.s.post(f"{api.base}/booking", data="not json", timeout=20)
    assert response.status_code == 400


def test_auth_with_empty_body_gives_no_token(api):
    response = api.s.post(f"{api.base}/auth", json={}, timeout=20)
    assert response.status_code == 200
    assert "token" not in response.json()


@pytest.mark.known_bug
@pytest.mark.xfail(strict=True, reason="a booking with missing fields crashes the server (500) instead of a 400")
def test_incomplete_booking_is_a_client_error(api):
    assert api.create({"firstname": "Ana"}).status_code == 400
