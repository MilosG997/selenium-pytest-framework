import json
from pathlib import Path

import pytest

from pages.saucedemo.pages import LoginPage

DATA = json.loads((Path(__file__).parents[3] / "data" / "saucedemo.json").read_text(encoding="utf-8"))


@pytest.fixture
def data():
    return DATA


@pytest.fixture
def shop(driver):
    """Logged in as standard_user, on the products page."""
    inventory = LoginPage(driver).open().login("standard_user")
    assert inventory.is_open()
    return inventory


@pytest.fixture
def login_as(driver):
    def _login(username):
        inventory = LoginPage(driver).open().login(username)
        assert inventory.is_open()
        return inventory
    return _login
