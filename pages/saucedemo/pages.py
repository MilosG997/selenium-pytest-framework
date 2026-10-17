"""Page objects for SauceDemo (https://www.saucedemo.com), a public demo shop made for test practice."""
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage, data_test

BASE = "https://www.saucedemo.com"
PASSWORD = "secret_sauce"  # published on the demo's own login page


def slug(product_name):
    """'Sauce Labs Bike Light' -> 'sauce-labs-bike-light' (how SauceDemo builds data-test ids)."""
    return product_name.lower().replace(" ", "-")


class Header(BasePage):
    CART_LINK = data_test("shopping-cart-link")
    CART_BADGE = data_test("shopping-cart-badge")
    MENU = (By.ID, "react-burger-menu-btn")
    LOGOUT = data_test("logout-sidebar-link")
    RESET = data_test("reset-sidebar-link")
    TITLE = data_test("title")

    def cart_count(self):
        badges = self.find_all(self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        self.click(self.CART_LINK)
        return CartPage(self.driver)

    def _menu(self, item):
        self.click(self.MENU)
        self.click(item)

    def logout(self):
        self._menu(self.LOGOUT)
        return LoginPage(self.driver)

    def reset_app_state(self):
        self._menu(self.RESET)


class LoginPage(BasePage):
    URL = BASE + "/"
    USERNAME = data_test("username")
    PASSWORD_FIELD = data_test("password")
    SUBMIT = data_test("login-button")
    ERROR = data_test("error")

    def login(self, username, password=PASSWORD):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD_FIELD, password)
        self.click(self.SUBMIT)
        return InventoryPage(self.driver)

    def error(self):
        return self.text(self.ERROR)

    def is_open(self):
        return self.is_visible(self.SUBMIT)


class InventoryPage(Header):
    URL = BASE + "/inventory.html"
    ITEM = data_test("inventory-item")
    NAME = data_test("inventory-item-name")
    PRICE = data_test("inventory-item-price")
    SORT = data_test("product-sort-container")
    IMAGES = (By.CSS_SELECTOR, "img.inventory_item_img")

    def is_open(self):
        return self.is_visible(self.ITEM, timeout=10)

    def names(self):
        return [e.text for e in self.find_all(self.NAME)]

    def prices(self):
        return [float(e.text.lstrip("$")) for e in self.find_all(self.PRICE)]

    def image_sources(self):
        return [e.get_attribute("src") for e in self.find_all(self.IMAGES)]

    def sort_by(self, value):
        """value: az, za, lohi, hilo"""
        Select(self.find(self.SORT)).select_by_value(value)

    def add(self, product_name):
        self.click(data_test(f"add-to-cart-{slug(product_name)}"))

    def remove(self, product_name):
        self.click(data_test(f"remove-{slug(product_name)}"))

    def button_text(self, product_name):
        item = self.find((By.XPATH, f'//*[@data-test="inventory-item"][.//*[text()="{product_name}"]]'))
        return item.find_element(By.TAG_NAME, "button").text

    def open_product(self, product_name):
        self.click((By.XPATH, f'//*[@data-test="inventory-item-name"][text()="{product_name}"]'))
        return ProductPage(self.driver)


class ProductPage(Header):
    NAME = data_test("inventory-item-name")
    PRICE = data_test("inventory-item-price")
    ADD = data_test("add-to-cart")
    BACK = data_test("back-to-products")

    def name(self):
        return self.text(self.NAME)

    def price(self):
        return float(self.text(self.PRICE).lstrip("$"))

    def add(self):
        self.click(self.ADD)

    def back(self):
        self.click(self.BACK)
        return InventoryPage(self.driver)


class CartPage(Header):
    URL = BASE + "/cart.html"
    ITEM_NAME = data_test("inventory-item-name")
    CHECKOUT = data_test("checkout")
    CONTINUE = data_test("continue-shopping")

    def names(self):
        # React re-renders the list after a change; read again if an element went stale mid-read
        for _ in range(3):
            try:
                return [e.text for e in self.find_all(self.ITEM_NAME)]
            except StaleElementReferenceException:
                continue
        return [e.text for e in self.find_all(self.ITEM_NAME)]

    def remove(self, product_name):
        button = data_test(f"remove-{slug(product_name)}")
        self.click(button)
        self.wait.until(EC.invisibility_of_element_located(button))

    def checkout(self):
        self.click(self.CHECKOUT)
        return CheckoutInfoPage(self.driver)

    def continue_shopping(self):
        self.click(self.CONTINUE)
        return InventoryPage(self.driver)


class CheckoutInfoPage(Header):
    FIRST = data_test("firstName")
    LAST = data_test("lastName")
    ZIP = data_test("postalCode")
    CONTINUE = data_test("continue")
    CANCEL = data_test("cancel")
    ERROR = data_test("error")

    def fill(self, first, last, postal_code):
        self.type(self.FIRST, first)
        self.type(self.LAST, last)
        self.type(self.ZIP, postal_code)
        return self

    def field_value(self, locator):
        return self.find(locator).get_attribute("value")

    def continue_(self):
        self.click(self.CONTINUE)
        return CheckoutOverviewPage(self.driver)

    def error(self):
        return self.text(self.ERROR)


class CheckoutOverviewPage(Header):
    ITEM_NAME = data_test("inventory-item-name")
    ITEM_PRICE = data_test("inventory-item-price")
    SUBTOTAL = data_test("subtotal-label")
    TAX = data_test("tax-label")
    TOTAL = data_test("total-label")
    FINISH = data_test("finish")

    @staticmethod
    def _amount(label):
        return float(label.split("$")[1])

    def item_prices(self):
        return [float(e.text.lstrip("$")) for e in self.find_all(self.ITEM_PRICE)]

    def subtotal(self):
        return self._amount(self.text(self.SUBTOTAL))

    def tax(self):
        return self._amount(self.text(self.TAX))

    def total(self):
        return self._amount(self.text(self.TOTAL))

    def finish(self):
        self.click(self.FINISH)
        return CompletePage(self.driver)


class CompletePage(Header):
    HEADER = data_test("complete-header")

    def message(self):
        return self.text(self.HEADER)

    def is_open(self):
        return self.wait.until(EC.url_contains("checkout-complete")) and self.is_visible(self.HEADER)
