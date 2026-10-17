import json
from pathlib import Path

import pytest

from pages.saucedemo.pages import InventoryPage, LoginPage

DATA = json.loads((Path(__file__).parents[3] / "data" / "saucedemo.json").read_text(encoding="utf-8"))


@pytest.mark.smoke
def test_standard_user_can_log_in(driver):
    inventory = LoginPage(driver).open().login("standard_user")
    assert inventory.is_open()
    assert inventory.text(inventory.TITLE) == "Products"


@pytest.mark.regression
@pytest.mark.parametrize("username", DATA["users_that_can_log_in"])
def test_every_active_user_reaches_products(driver, username):
    assert LoginPage(driver).open().login(username).is_open()


@pytest.mark.regression
@pytest.mark.parametrize("case", DATA["login_errors"], ids=lambda c: c["id"])
def test_login_shows_the_right_error(driver, case):
    page = LoginPage(driver).open()
    page.login(case["username"], case["password"])
    assert page.error() == case["error"]
    assert "inventory" not in driver.current_url


@pytest.mark.regression
def test_products_page_is_protected_without_login(driver):
    driver.get(InventoryPage.URL)
    page = LoginPage(driver)
    assert page.is_open()
    assert "You can only access '/inventory.html' when you are logged in" in page.error()


@pytest.mark.smoke
def test_logout_returns_to_login_and_blocks_back_button(shop, driver):
    login = shop.logout()
    assert login.is_open()
    driver.back()
    assert LoginPage(driver).is_open(), "after logout the products page must not be reachable"
