"""Base class for all page objects: explicit waits only, no sleeps."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def norm(text):
    """Collapse whitespace. Firefox returns raw DOM text (double spaces, no CSS uppercase), Chrome the rendered one."""
    return " ".join(text.split())


def data_test(value):
    """Locator for elements with a data-test attribute (SauceDemo uses them everywhere)."""
    return By.CSS_SELECTOR, f'[data-test="{value}"]'


class BasePage:
    URL = ""
    TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    def open(self):
        self.driver.get(self.URL)
        return self

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text):
        field = self.find(locator)
        field.clear()
        field.send_keys(text)

    def text(self, locator):
        return self.find(locator).text

    def is_visible(self, locator, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def wait_for_url(self, part):
        self.wait.until(EC.url_contains(part))
