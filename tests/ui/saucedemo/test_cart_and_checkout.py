import json
from pathlib import Path

import pytest

DATA = json.loads((Path(__file__).parents[3] / "data" / "saucedemo.json").read_text(encoding="utf-8"))
PICK = ["Sauce Labs Backpack", "Sauce Labs Bolt T-Shirt", "Sauce Labs Fleece Jacket"]


@pytest.mark.regression
def test_cart_contains_exactly_what_was_added(shop):
    for name in PICK:
        shop.add(name)
    cart = shop.open_cart()
    assert sorted(cart.names()) == sorted(PICK)


@pytest.mark.regression
def test_cart_survives_navigation(shop):
    shop.add("Sauce Labs Backpack")
    cart = shop.open_cart()
    inventory = cart.continue_shopping()
    assert inventory.cart_count() == 1
    assert inventory.open_cart().names() == ["Sauce Labs Backpack"]


@pytest.mark.regression
def test_remove_from_cart(shop):
    shop.add("Sauce Labs Backpack")
    shop.add("Sauce Labs Onesie")
    cart = shop.open_cart()
    cart.remove("Sauce Labs Backpack")
    assert cart.names() == ["Sauce Labs Onesie"]
    assert cart.cart_count() == 1


@pytest.mark.regression
@pytest.mark.parametrize("case", DATA["checkout_errors"], ids=lambda c: c["id"])
def test_checkout_requires_all_fields(shop, case):
    shop.add("Sauce Labs Backpack")
    info = shop.open_cart().checkout()
    info.fill(case["first"], case["last"], case["zip"])
    info.continue_()
    assert info.error() == case["error"]


@pytest.mark.regression
def test_order_totals_add_up(shop, data):
    for name in PICK:
        shop.add(name)
    c = data["customer"]
    overview = shop.open_cart().checkout().fill(c["first"], c["last"], c["zip"]).continue_()
    items = overview.item_prices()
    assert overview.subtotal() == pytest.approx(sum(items))
    assert overview.tax() == pytest.approx(round(sum(items) * data["tax_rate"], 2))
    assert overview.total() == pytest.approx(overview.subtotal() + overview.tax())


@pytest.mark.smoke
def test_complete_purchase_end_to_end(shop, data):
    shop.add("Sauce Labs Bike Light")
    c = data["customer"]
    overview = shop.open_cart().checkout().fill(c["first"], c["last"], c["zip"]).continue_()
    done = overview.finish()
    assert done.is_open()
    assert done.message() == "Thank you for your order!"
    assert done.cart_count() == 0, "cart must be empty after the order"


@pytest.mark.known_bug
@pytest.mark.xfail(strict=True, reason="error_user: the Last Name field ignores typing")
def test_error_user_can_type_last_name(login_as, data):
    inventory = login_as("error_user")
    inventory.add("Sauce Labs Backpack")
    info = inventory.open_cart().checkout()
    info.fill("Ana", "Petrovic", "11000")
    assert info.field_value(info.LAST) == "Petrovic"
