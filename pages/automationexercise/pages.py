"""Page objects for Automation Exercise (https://automationexercise.com), a full demo shop made for test practice."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage

BASE = "https://automationexercise.com"


def qa(value):
    return By.CSS_SELECTOR, f'[data-qa="{value}"]'


def price(text):
    """'Rs. 1,500' -> 1500"""
    return int(text.replace("Rs.", "").replace(",", "").strip())


class AEPage(BasePage):
    """Shared header/footer. Ads are blocked in Chrome/Edge; for Firefox they are removed from the page."""
    LOGGED_IN_AS = (By.XPATH, "//a[contains(., 'Logged in as')]")
    LOGOUT = (By.CSS_SELECTOR, "a[href='/logout']")
    DELETE_ACCOUNT = (By.CSS_SELECTOR, "a[href='/delete_account']")
    SUBSCRIBE_EMAIL = (By.ID, "susbscribe_email")  # (sic) the site's own spelling
    SUBSCRIBE = (By.ID, "subscribe")
    SUBSCRIBED = (By.ID, "success-subscribe")
    SCROLL_UP = (By.ID, "scrollUp")
    HERO_TEXT = (By.CSS_SELECTOR, "#slider-carousel .item.active h2")

    def go(self, path):
        self.driver.get(BASE + path)
        if "#google_vignette" in self.driver.current_url:  # full-screen ad interstitial
            self.driver.get(BASE + path)
        self.hide_ads()
        return self

    def open(self):
        return self.go(self.URL)

    def hide_ads(self):
        self.driver.execute_script(
            "document.querySelectorAll('ins.adsbygoogle, iframe[id^=aswift], iframe[src*=googlesyndication],"
            " #ad_position_box, .google-auto-placed').forEach(e => e.remove())")

    def click(self, locator):
        """Scroll into view first and fall back to a JS click if something still overlaps the element."""
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", el)
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except Exception:
            self.driver.execute_script("arguments[0].click()", el)

    def logged_in_as(self):
        return self.text(self.LOGGED_IN_AS).replace("Logged in as", "").strip()

    def subscribe(self, email):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        self.type(self.SUBSCRIBE_EMAIL, email)
        self.click(self.SUBSCRIBE)
        return self.text(self.SUBSCRIBED)


class HomePage(AEPage):
    URL = "/"


class LoginSignupPage(AEPage):
    URL = "/login"
    LOGIN_EMAIL, LOGIN_PASSWORD, LOGIN_BUTTON = qa("login-email"), qa("login-password"), qa("login-button")
    SIGNUP_NAME, SIGNUP_EMAIL, SIGNUP_BUTTON = qa("signup-name"), qa("signup-email"), qa("signup-button")
    ERROR = (By.CSS_SELECTOR, "form p[style*='color: red']")

    def login(self, email, password):
        self.type(self.LOGIN_EMAIL, email)
        self.type(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def start_signup(self, name, email):
        self.type(self.SIGNUP_NAME, name)
        self.type(self.SIGNUP_EMAIL, email)
        self.click(self.SIGNUP_BUTTON)
        return SignupPage(self.driver)

    def error(self):
        return self.text(self.ERROR)


class SignupPage(AEPage):
    CREATE = qa("create-account")
    CREATED = qa("account-created")
    CONTINUE = qa("continue-button")
    DELETED = qa("account-deleted")

    def fill_and_create(self, user):
        self.wait_for_url("/signup")
        self.click((By.ID, "id_gender2" if user["title"] == "Mrs" else "id_gender1"))
        self.type(qa("password"), user["password"])
        Select(self.find(qa("days"))).select_by_value(user["birth"][0])
        Select(self.find(qa("months"))).select_by_value(user["birth"][1])
        Select(self.find(qa("years"))).select_by_value(user["birth"][2])
        for field in ("first_name", "last_name", "company", "address", "state", "city", "zipcode", "mobile_number"):
            self.type(qa(field), user[field])
        Select(self.find(qa("country"))).select_by_visible_text(user["country"])
        self.click(self.CREATE)
        return self.text(self.CREATED)

    def continue_(self):
        self.click(self.CONTINUE)
        return HomePage(self.driver)


class ProductsPage(AEPage):
    URL = "/products"
    CARD = (By.CSS_SELECTOR, ".features_items .product-image-wrapper")
    CARD_NAME = (By.CSS_SELECTOR, ".features_items .productinfo p")
    CARD_PRICE = (By.CSS_SELECTOR, ".features_items .productinfo h2")
    SEARCH = (By.ID, "search_product")
    SEARCH_GO = (By.ID, "submit_search")
    TITLE = (By.CSS_SELECTOR, ".features_items h2.title")
    MODAL = (By.ID, "cartModal")
    CONTINUE = (By.CSS_SELECTOR, "#cartModal .close-modal")
    VIEW_CART = (By.CSS_SELECTOR, "#cartModal a[href='/view_cart']")

    def names(self):
        return [e.text for e in self.find_all(self.CARD_NAME)]

    def prices(self):
        return [price(e.text) for e in self.find_all(self.CARD_PRICE)]

    def title(self):
        return self.text(self.TITLE)

    def search(self, term):
        self.type(self.SEARCH, term)
        self.click(self.SEARCH_GO)
        return self

    def add_to_cart(self, product_id, then_view_cart=False):
        self.click((By.CSS_SELECTOR, f".productinfo a.add-to-cart[data-product-id='{product_id}']"))
        self.find(self.MODAL)
        self.click(self.VIEW_CART if then_view_cart else self.CONTINUE)
        if not then_view_cart:
            self.wait.until(EC.invisibility_of_element_located(self.MODAL))
        return CartPage(self.driver) if then_view_cart else self

    def open_category(self, top, sub):
        """top: Women/Men/Kids, sub: e.g. Dress, Tops, Jeans"""
        self.click((By.CSS_SELECTOR, f"a[href='#{top}']"))
        self.click((By.XPATH, f"//div[@id='{top}']//a[normalize-space()='{sub}']"))
        return self

    def open_brand(self, brand):
        self.click((By.CSS_SELECTOR, f".brands-name a[href='/brand_products/{brand}']"))
        return self

    def open_product(self, product_id):
        return ProductDetailPage(self.driver).go(f"/product_details/{product_id}")


class ProductDetailPage(AEPage):
    INFO = (By.CSS_SELECTOR, ".product-information")
    NAME = (By.CSS_SELECTOR, ".product-information h2")
    PRICE = (By.CSS_SELECTOR, ".product-information span span")
    QUANTITY = (By.ID, "quantity")
    ADD = (By.CSS_SELECTOR, "button.cart")
    REVIEW_NAME, REVIEW_EMAIL, REVIEW_TEXT, REVIEW_SEND = (By.ID, "name"), (By.ID, "email"), (By.ID, "review"), (By.ID, "button-review")
    REVIEW_OK = (By.CSS_SELECTOR, "#review-section .alert-success")

    def info(self):
        """{'Category': 'Women > Tops', 'Availability': 'In Stock', 'Condition': 'New', 'Brand': 'Polo'}"""
        lines = [p.text for p in self.find(self.INFO).find_elements(By.TAG_NAME, "p")]
        return dict(line.split(":", 1) for line in lines if ":" in line) | {"name": self.text(self.NAME)}

    def price(self):
        return price(self.text(self.PRICE))

    def add(self, quantity):
        self.type(self.QUANTITY, str(quantity))
        self.click(self.ADD)
        self.find(ProductsPage.MODAL)
        self.click(ProductsPage.VIEW_CART)
        return CartPage(self.driver)

    def review(self, name, email, text):
        self.type(self.REVIEW_NAME, name)
        self.type(self.REVIEW_EMAIL, email)
        self.type(self.REVIEW_TEXT, text)
        self.click(self.REVIEW_SEND)
        return self.wait.until(EC.visibility_of_element_located(self.REVIEW_OK)).text


class CartPage(AEPage):
    URL = "/view_cart"
    ROW = (By.CSS_SELECTOR, "#cart_info_table tbody tr[id^='product-']")
    EMPTY = (By.ID, "empty_cart")

    def rows(self):
        self.wait_for_url("/view_cart")
        out = []
        for r in self.find_all(self.ROW):
            out.append({
                "id": r.get_attribute("id").replace("product-", ""),
                "name": r.find_element(By.CSS_SELECTOR, ".cart_description h4 a").text,
                "price": price(r.find_element(By.CSS_SELECTOR, ".cart_price p").text),
                "quantity": int(r.find_element(By.CSS_SELECTOR, ".cart_quantity button").text),
                "total": price(r.find_element(By.CSS_SELECTOR, ".cart_total_price").text),
            })
        return out

    def remove(self, product_id):
        self.click((By.CSS_SELECTOR, f".cart_quantity_delete[data-product-id='{product_id}']"))
        self.wait.until(EC.invisibility_of_element_located((By.ID, f"product-{product_id}")))

    def is_empty(self):
        return self.is_visible(self.EMPTY, timeout=5)


class ContactPage(AEPage):
    URL = "/contact_us"
    SUCCESS = (By.CSS_SELECTOR, "#contact-page .status.alert-success")

    def send(self, name, email, subject, message, file_path):
        for field, value in (("name", name), ("email", email), ("subject", subject), ("message", message)):
            self.type(qa(field), value)
        self.driver.find_element(By.NAME, "upload_file").send_keys(str(file_path))
        self.click(qa("submit-button"))
        self.wait.until(EC.alert_is_present()).accept()  # "Press OK to proceed!"
        return self.text(self.SUCCESS)
