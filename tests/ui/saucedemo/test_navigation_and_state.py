"""SauceDemo navigation, menu, footer links and state that must survive reloads."""
import pytest
from selenium.webdriver.common.by import By

from pages.base_page import data_test
from pages.saucedemo.pages import InventoryPage, LoginPage

pytestmark = pytest.mark.regression


@pytest.fixture
def shop(driver):
    return LoginPage(driver).open().login("standard_user")


def test_cart_badge_survives_a_page_reload(shop, driver):
    shop.add("Sauce Labs Backpack")
    shop.add("Sauce Labs Onesie")
    driver.refresh()
    assert InventoryPage(driver).cart_count() == 2


def test_cart_contents_survive_logout_and_login(shop, driver):
    shop.add("Sauce Labs Bike Light")
    login = shop.logout()
    assert login.is_open(), "the sidebar slides in: make sure logout really landed on the login page"
    inventory = login.login("standard_user")
    assert inventory.is_open(), "wait for the catalog before opening the cart (flaky under parallel load)"
    assert inventory.cart_count() == 1
    cart = inventory.open_cart()
    cart.wait_for_url("/cart.html")
    assert cart.names() == ["Sauce Labs Bike Light"]


def test_button_text_switches_between_add_and_remove(shop):
    assert shop.button_text("Sauce Labs Fleece Jacket") == "Add to cart"
    shop.add("Sauce Labs Fleece Jacket")
    assert shop.button_text("Sauce Labs Fleece Jacket") == "Remove"


def test_product_page_back_button(shop):
    page = shop.open_product("Sauce Labs Bolt T-Shirt")
    assert page.name() == "Sauce Labs Bolt T-Shirt"
    assert page.back().is_open()


def test_add_from_product_page_then_remove_in_catalog(shop):
    page = shop.open_product("Sauce Labs Onesie")
    page.add()
    inventory = page.back()
    assert inventory.cart_count() == 1
    inventory.remove("Sauce Labs Onesie")
    assert inventory.cart_count() == 0


def test_continue_shopping_returns_to_catalog(shop):
    shop.add("Sauce Labs Backpack")
    inventory = shop.open_cart().continue_shopping()
    assert inventory.is_open()
    assert inventory.cart_count() == 1


def test_cancel_checkout_keeps_the_cart(shop, driver):
    shop.add("Sauce Labs Backpack")
    info = shop.open_cart().checkout()
    info.click(info.CANCEL)
    assert driver.current_url.endswith("/cart.html")
    assert info.open_cart().names() == ["Sauce Labs Backpack"]


def test_menu_about_points_to_sauce_labs(shop):
    shop.click(shop.MENU)
    about = shop.find(data_test("about-sidebar-link"))
    assert about.get_attribute("href").startswith("https://saucelabs.com")


def test_menu_all_items_returns_to_catalog(shop, driver):
    shop.open_cart()
    shop.click(shop.MENU)
    shop.click(data_test("inventory-sidebar-link"))
    assert InventoryPage(driver).is_open()


@pytest.mark.parametrize("network,domain", [("x", "x.com"), ("facebook", "facebook.com"), ("linkedin", "linkedin.com")])
def test_footer_social_links(shop, network, domain):
    link = shop.find(data_test(f"social-{network}"))
    assert link.get_attribute("href").startswith(f"https://{domain}") or f".{domain}" in link.get_attribute("href")
    assert link.get_attribute("target") == "_blank"


def test_footer_shows_the_current_year_copyright(shop):
    text = shop.text(data_test("footer-copy"))
    assert "Sauce Labs" in text and "All Rights Reserved" in text


@pytest.mark.parametrize("path", ["/cart.html", "/checkout-step-one.html", "/checkout-step-two.html",
                                  "/checkout-complete.html", "/inventory-item.html?id=4"])
def test_every_inner_page_requires_login(driver, path):
    driver.get("https://www.saucedemo.com" + path)
    page = LoginPage(driver)
    assert page.is_open()
    assert "You can only access" in page.error()


def test_performance_glitch_user_still_gets_in(driver):
    """This user is slow on purpose: an explicit wait copes with it, a fixed sleep would be flaky."""
    inventory = LoginPage(driver).open().login("performance_glitch_user")
    assert inventory.is_open()
    assert len(inventory.names()) == 6


def test_every_product_has_name_price_and_image(shop):
    items = shop.find_all(shop.ITEM)
    assert len(items) == 6
    for item in items:
        assert item.find_element(*shop.NAME).text
        assert item.find_element(*shop.PRICE).text.startswith("$")
        assert item.find_element(By.TAG_NAME, "img").get_attribute("src")


@pytest.mark.known_bug
@pytest.mark.xfail(strict=True, reason="visual_user: the catalog shows different prices than standard_user")
def test_visual_user_sees_the_same_prices(driver):
    standard = LoginPage(driver).open().login("standard_user").prices()
    driver.delete_all_cookies()
    driver.execute_script("localStorage.clear()")
    visual = LoginPage(driver).open().login("visual_user").prices()
    assert visual == standard
