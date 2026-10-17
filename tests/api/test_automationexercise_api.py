"""Automation Exercise public API: catalog, search, login check, full account lifecycle, wrong methods."""
import pytest
from jsonschema import validate

from api.automationexercise import AEClient, fake_user

pytestmark = pytest.mark.api

PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "price", "brand", "category"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1},
        "price": {"type": "string", "pattern": r"^Rs\. \d+$"},
        "brand": {"type": "string", "minLength": 1},
        "category": {"type": "object", "required": ["usertype", "category"]},
    },
}


@pytest.fixture(scope="module")
def api():
    return AEClient()


@pytest.mark.smoke
def test_products_list(api):
    _, body = api.products()
    assert body["responseCode"] == 200
    assert len(body["products"]) > 0
    for product in body["products"]:
        validate(product, PRODUCT_SCHEMA)
    ids = [p["id"] for p in body["products"]]
    assert len(ids) == len(set(ids)), "product ids must be unique"


def test_brands_list_covers_every_product_brand(api):
    brands = {b["brand"] for b in api.brands()[1]["brands"]}
    assert {p["brand"] for p in api.products()[1]["products"]} <= brands


@pytest.mark.parametrize("term", ["top", "tshirt", "jean"])
def test_search_results_contain_the_term(api, term):
    _, body = api.search(term)
    assert body["responseCode"] == 200
    assert body["products"]
    for p in body["products"]:
        haystack = f'{p["name"]} {p["category"]["category"]}'.lower().replace("-", "").replace(" ", "")
        assert term in haystack


@pytest.mark.parametrize("call, expected", [
    (lambda a: a.call("POST", "productsList"), (405, "This request method is not supported.")),
    (lambda a: a.call("PUT", "brandsList"), (405, "This request method is not supported.")),
    (lambda a: a.call("DELETE", "verifyLogin"), (405, "This request method is not supported.")),
    (lambda a: a.search(), (400, "Bad request, search_product parameter is missing in POST request.")),
    (lambda a: a.verify_login(password="x"), (400, "Bad request, email or password parameter is missing in POST request.")),
    (lambda a: a.verify_login("nobody-qa@example.com", "x"), (404, "User not found!")),
], ids=["post_products", "put_brands", "delete_verify_login", "search_without_term",
        "login_without_email", "login_unknown_user"])
def test_error_responses(api, call, expected):
    _, body = call(api)
    assert (body["responseCode"], body["message"]) == expected


@pytest.mark.smoke
def test_account_lifecycle(api):
    """create -> login check -> read -> update -> delete -> gone"""
    user = fake_user()
    try:
        assert api.create_account(user)[1] == {"responseCode": 201, "message": "User created!"}
        assert api.verify_login(user["email"], user["password"])[1]["message"] == "User exists!"

        detail = api.user_detail(user["email"])[1]["user"]
        assert (detail["email"], detail["first_name"], detail["city"]) == (user["email"], "QA", "Toronto")

        assert api.update_account(dict(user, city="Ottawa"))[1]["message"] == "User updated!"
        assert api.user_detail(user["email"])[1]["user"]["city"] == "Ottawa"

        assert api.verify_login(user["email"], "wrong-password")[1]["message"] == "User not found!"
    finally:
        _, body = api.delete_account(user["email"], user["password"])
    assert body == {"responseCode": 200, "message": "Account deleted!"}
    assert api.verify_login(user["email"], user["password"])[1]["message"] == "User not found!"


def test_duplicate_account_is_rejected(api):
    user = fake_user()
    try:
        api.create_account(user)
        assert api.create_account(user)[1] == {"responseCode": 400, "message": "Email already exists!"}
    finally:
        api.delete_account(user["email"], user["password"])


@pytest.mark.known_bug
@pytest.mark.xfail(strict=True, reason="API always answers HTTP 200; the real status is only inside the JSON body")
def test_http_status_matches_response_code(api):
    status, body = api.verify_login("nobody-qa@example.com", "x")
    assert status == body["responseCode"] == 404
