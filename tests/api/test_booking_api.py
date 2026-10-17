"""REST API tests: auth, CRUD, schema validation and negative cases on Restful-Booker."""
import json
import uuid
from pathlib import Path

import pytest
from jsonschema import validate

from api.booker import BookerClient

pytestmark = pytest.mark.api
SCHEMA = json.loads((Path(__file__).parents[2] / "data" / "booking_schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def api():
    client = BookerClient()
    if client.s.get(f"{client.base}/ping", timeout=20).status_code != 201:
        pytest.skip("Restful-Booker is down")
    return client


@pytest.fixture(scope="module")
def token(api):
    return api.token().json()["token"]


@pytest.fixture
def new_booking():
    return {"firstname": "Ana", "lastname": f"QA-{uuid.uuid4().hex[:8]}", "totalprice": 240, "depositpaid": True,
            "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"}, "additionalneeds": "Breakfast"}


@pytest.fixture
def created(api, token, new_booking):
    r = api.create(new_booking)
    booking_id = r.json()["bookingid"]
    yield booking_id, new_booking
    api.delete(booking_id, token)  # clean up even if the test failed


@pytest.mark.smoke
def test_auth_returns_token(api):
    r = api.token()
    assert r.status_code == 200
    assert len(r.json()["token"]) > 10


def test_auth_with_bad_credentials(api):
    r = api.token(password="wrong")
    assert r.json() == {"reason": "Bad credentials"}


@pytest.mark.smoke
def test_create_booking_matches_schema_and_input(api, new_booking, token):
    r = api.create(new_booking)
    assert r.status_code == 200
    body = r.json()
    validate(body["booking"], SCHEMA)
    assert body["booking"] == new_booking
    api.delete(body["bookingid"], token)


def test_get_booking_by_id(api, created):
    booking_id, data = created
    r = api.get(booking_id)
    assert r.status_code == 200
    validate(r.json(), SCHEMA)
    assert r.json()["lastname"] == data["lastname"]


def test_filter_by_name_finds_the_booking(api, created):
    booking_id, data = created
    ids = [b["bookingid"] for b in api.list(firstname=data["firstname"], lastname=data["lastname"]).json()]
    assert booking_id in ids


def test_full_update_with_token(api, created, token):
    booking_id, data = created
    changed = dict(data, totalprice=999, depositpaid=False)
    r = api.update(booking_id, changed, token)
    assert r.status_code == 200
    assert r.json() == changed


def test_partial_update_changes_only_given_fields(api, created, token):
    booking_id, data = created
    r = api.patch(booking_id, {"additionalneeds": "Late checkout"}, token)
    assert r.status_code == 200
    assert r.json() == dict(data, additionalneeds="Late checkout")


@pytest.mark.parametrize("method", ["update", "patch", "delete"])
def test_changes_without_token_are_forbidden(api, created, method):
    booking_id, data = created
    args = {"update": (booking_id, data), "patch": (booking_id, {"totalprice": 1}), "delete": (booking_id,)}[method]
    assert getattr(api, method)(*args).status_code == 403
    assert api.get(booking_id).json()["totalprice"] == data["totalprice"], "data must stay unchanged"


def test_delete_then_booking_is_gone(api, new_booking, token):
    booking_id = api.create(new_booking).json()["bookingid"]
    assert api.delete(booking_id, token).status_code == 201
    assert api.get(booking_id).status_code == 404


def test_unknown_booking_returns_404(api):
    assert api.get(999999999).status_code == 404
