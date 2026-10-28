"""Page objects for The Internet (https://the-internet.herokuapp.com), a public collection of tricky UI widgets."""
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from pages.base_page import BasePage

BASE = "https://the-internet.herokuapp.com"
FLASH = (By.ID, "flash")


class CheckboxesPage(BasePage):
    URL = BASE + "/checkboxes"
    BOXES = (By.CSS_SELECTOR, "#checkboxes input[type=checkbox]")

    def states(self):
        return [b.is_selected() for b in self.find_all(self.BOXES)]

    def toggle(self, index):
        self.find_all(self.BOXES)[index].click()


class DropdownPage(BasePage):
    URL = BASE + "/dropdown"
    SELECT = (By.ID, "dropdown")

    def choose(self, text):
        Select(self.find(self.SELECT)).select_by_visible_text(text)

    def selected(self):
        return Select(self.find(self.SELECT)).first_selected_option.text


class DynamicLoadingPage(BasePage):
    """Example 1: element is hidden in the DOM. Example 2: element is rendered only after loading."""
    START = (By.CSS_SELECTOR, "#start button")
    RESULT = (By.CSS_SELECTOR, "#finish h4")

    def open_example(self, number):
        self.driver.get(f"{BASE}/dynamic_loading/{number}")
        return self

    def start_and_wait(self, timeout=15):
        self.click(self.START)
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.RESULT)).text


class DynamicControlsPage(BasePage):
    URL = BASE + "/dynamic_controls"
    CHECKBOX = (By.CSS_SELECTOR, "#checkbox-example input[type=checkbox]")
    TOGGLE_CHECKBOX = (By.CSS_SELECTOR, "#checkbox-example button")
    INPUT = (By.CSS_SELECTOR, "#input-example input")
    TOGGLE_INPUT = (By.CSS_SELECTOR, "#input-example button")
    MESSAGE = (By.ID, "message")

    def remove_checkbox(self):
        self.click(self.TOGGLE_CHECKBOX)
        self.wait.until(EC.invisibility_of_element_located(self.CHECKBOX))
        return self.text(self.MESSAGE)

    def enable_input(self):
        self.click(self.TOGGLE_INPUT)
        self.wait.until(EC.element_to_be_clickable(self.INPUT))
        return self.text(self.MESSAGE)


class AlertsPage(BasePage):
    URL = BASE + "/javascript_alerts"
    RESULT = (By.ID, "result")

    def _button(self, label):
        self.click((By.XPATH, f"//button[text()='{label}']"))
        return self.wait.until(EC.alert_is_present())

    def js_alert(self):
        self._button("Click for JS Alert").accept()
        return self.text(self.RESULT)

    def js_confirm(self, accept):
        alert = self._button("Click for JS Confirm")
        alert.accept() if accept else alert.dismiss()
        return self.text(self.RESULT)

    def js_prompt(self, answer):
        alert = self._button("Click for JS Prompt")
        alert.send_keys(answer)
        alert.accept()
        return self.text(self.RESULT)


class WindowsPage(BasePage):
    URL = BASE + "/windows"
    LINK = (By.LINK_TEXT, "Click Here")

    def open_new_window(self):
        original = self.driver.current_window_handle
        self.click(self.LINK)
        self.wait.until(EC.number_of_windows_to_be(2))
        new = next(h for h in self.driver.window_handles if h != original)
        self.driver.switch_to.window(new)
        heading = self.text((By.TAG_NAME, "h3"))
        return original, heading


class NestedFramesPage(BasePage):
    URL = BASE + "/nested_frames"

    def frame_text(self, *path):
        """path like ('frame-top', 'frame-middle')."""
        self.driver.switch_to.default_content()
        for name in path:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, name)))
        text = self.driver.find_element(By.TAG_NAME, "body").text.strip()
        self.driver.switch_to.default_content()
        return text


class HoversPage(BasePage):
    URL = BASE + "/hovers"
    FIGURES = (By.CLASS_NAME, "figure")

    def hover_caption(self, index):
        figure = self.find_all(self.FIGURES)[index]
        ActionChains(self.driver).move_to_element(figure).perform()
        caption = figure.find_element(By.CSS_SELECTOR, ".figcaption h5")
        self.wait.until(EC.visibility_of(caption))
        return caption.text


class DragAndDropPage(BasePage):
    """HTML5 drag-and-drop: ActionChains cannot trigger it in Chrome, so the drag events are dispatched in JS."""
    URL = BASE + "/drag_and_drop"
    HEADERS = (By.CSS_SELECTOR, "#columns .column header")
    _JS = """
    const [src, dst] = arguments; const data = new DataTransfer();
    for (const [el, type] of [[src,'dragstart'],[dst,'dragenter'],[dst,'dragover'],[dst,'drop'],[src,'dragend']])
      el.dispatchEvent(new DragEvent(type, {bubbles: true, cancelable: true, dataTransfer: data}));
    """

    def order(self):
        return [h.text for h in self.find_all(self.HEADERS)]

    def drag(self, source_id, target_id):
        src = self.find((By.ID, source_id))
        dst = self.find((By.ID, target_id))
        self.driver.execute_script(self._JS, src, dst)


class UploadPage(BasePage):
    URL = BASE + "/upload"
    INPUT = (By.ID, "file-upload")
    SUBMIT = (By.ID, "file-submit")
    RESULT = (By.ID, "uploaded-files")

    def upload(self, path):
        self.driver.find_element(*self.INPUT).send_keys(str(path))
        self.click(self.SUBMIT)
        return self.text(self.RESULT)


class TablesPage(BasePage):
    URL = BASE + "/tables"

    def column(self, header):
        headers = [h.text for h in self.find_all((By.CSS_SELECTOR, "#table1 thead th"))]
        i = headers.index(header) + 1
        return [c.text for c in self.find_all((By.CSS_SELECTOR, f"#table1 tbody tr td:nth-child({i})"))]

    def sort_by(self, header):
        self.click((By.XPATH, f"//table[@id='table1']//th/span[text()='{header}']"))


class AddRemovePage(BasePage):
    URL = BASE + "/add_remove_elements/"
    ADD = (By.XPATH, "//button[text()='Add Element']")
    DELETE = (By.CSS_SELECTOR, "#elements button")

    def add(self, times):
        for _ in range(times):
            self.click(self.ADD)

    def delete_one(self):
        self.find_all(self.DELETE)[0].click()

    def count(self):
        return len(self.find_all(self.DELETE))


class LoginFormPage(BasePage):
    URL = BASE + "/login"
    USER = "tomsmith"                 # demo credentials printed on the page itself
    PASSWORD = "SuperSecretPassword!"

    def login(self, username, password):
        self.type((By.ID, "username"), username)
        self.type((By.ID, "password"), password)
        self.click((By.CSS_SELECTOR, "button[type=submit]"))
        return self.text(FLASH)

    def logout(self):
        self.click((By.CSS_SELECTOR, "a[href='/logout']"))
        return self.text(FLASH)


class KeyPressesPage(BasePage):
    URL = BASE + "/key_presses"

    def press(self, key):
        self.find((By.ID, "target")).send_keys(key)
        return self.text((By.ID, "result"))


class ContextMenuPage(BasePage):
    URL = BASE + "/context_menu"

    def right_click_box(self):
        ActionChains(self.driver).context_click(self.find((By.ID, "hot-spot"))).perform()
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text


class BrokenImagesPage(BasePage):
    URL = BASE + "/broken_images"

    def broken(self):
        return self.driver.execute_script(
            "return [...document.querySelectorAll('.example img')]"
            ".filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src'))")


class ShadowDomPage(BasePage):
    URL = BASE + "/shadowdom"
    HOSTS = (By.TAG_NAME, "my-paragraph")

    def slotted_texts(self):
        return [h.text for h in self.find_all(self.HOSTS)]

    def slot_name(self):
        """The <slot> lives inside the shadow root, so it is only reachable through element.shadow_root."""
        root = self.find(self.HOSTS).shadow_root
        return root.find_element(By.CSS_SELECTOR, "slot").get_attribute("name")


class InfiniteScrollPage(BasePage):
    URL = BASE + "/infinite_scroll"
    BLOCKS = (By.CSS_SELECTOR, ".jscroll-added")

    def count(self):
        return len(self.find_all(self.BLOCKS))

    def scroll_until(self, at_least, timeout=20):
        def more(d):
            d.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            return self.count() >= at_least
        WebDriverWait(self.driver, timeout, poll_frequency=0.7).until(more)
        return self.count()


class FloatingMenuPage(BasePage):
    URL = BASE + "/floating_menu"
    MENU = (By.ID, "menu")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    def menu_top(self):
        return self.driver.execute_script("return arguments[0].getBoundingClientRect().top", self.find(self.MENU))


class SliderPage(BasePage):
    URL = BASE + "/horizontal_slider"
    SLIDER = (By.CSS_SELECTOR, "input[type=range]")
    VALUE = (By.ID, "range")

    def press(self, key, times):
        self.find(self.SLIDER).send_keys(key * times)
        return self.text(self.VALUE)


class NumberInputPage(BasePage):
    URL = BASE + "/inputs"
    INPUT = (By.CSS_SELECTOR, "input[type=number]")

    def press(self, key, times):
        field = self.find(self.INPUT)
        field.send_keys(key * times)
        return field.get_attribute("value")


class ChallengingDomPage(BasePage):
    """Ids change on every load, so the test locates by table structure and visible text only."""
    URL = BASE + "/challenging_dom"

    def headers(self):
        return [th.text for th in self.find_all((By.CSS_SELECTOR, "table thead th"))]

    def rows(self):
        return [[td.text for td in tr.find_elements(By.TAG_NAME, "td")]
                for tr in self.find_all((By.CSS_SELECTOR, "table tbody tr"))]


class LargeDomPage(BasePage):
    URL = BASE + "/large"

    def sibling(self, row, column):
        """The deep 'siblings' block: element N.M contains all later siblings, so read only its own text."""
        el = self.find((By.ID, f"sibling-{row}.{column}"))
        return self.driver.execute_script("return arguments[0].firstChild.textContent.trim()", el)

    def table_cell(self, row, column):
        return self.text((By.CSS_SELECTOR, f"#large-table tbody tr:nth-child({row}) td:nth-child({column})"))

    def table_size(self):
        rows = self.find_all((By.CSS_SELECTOR, "#large-table tbody tr"))
        return len(rows), len(self.find_all((By.CSS_SELECTOR, "#large-table thead th")))


class TinyMcePage(BasePage):
    URL = BASE + "/iframe"
    FRAME = (By.ID, "mce_0_ifr")

    def editor_text(self):
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.FRAME))
        text = self.find((By.ID, "tinymce")).text
        self.driver.switch_to.default_content()
        return text


class EntryAdPage(BasePage):
    URL = BASE + "/entry_ad"
    MODAL = (By.ID, "modal")
    CLOSE = (By.CSS_SELECTOR, "#modal .modal-footer p")

    def close_ad(self):
        self.click(self.CLOSE)
        self.wait.until(EC.invisibility_of_element_located(self.MODAL))


class GeolocationPage(BasePage):
    URL = BASE + "/geolocation"

    def where_am_i(self):
        self.click((By.XPATH, "//button[text()='Where am I?']"))
        return float(self.text((By.ID, "lat-value"))), float(self.text((By.ID, "long-value")))


class DynamicContentPage(BasePage):
    URL = BASE + "/dynamic_content?with_content=static"
    # the rows sit inside an outer .large-10 column too: take only the innermost ones
    TEXTS = (By.XPATH, "//div[@id='content']//div[contains(@class,'large-10')][not(.//div[contains(@class,'large-10')])]")

    def texts(self):
        return [e.text for e in self.find_all(self.TEXTS)]


class StatusCodesPage(BasePage):
    URL = BASE + "/status_codes"

    def code_links(self):
        return [a.get_attribute("href") for a in self.find_all((By.CSS_SELECTOR, "#content li a"))]


class RedirectorPage(BasePage):
    URL = BASE + "/redirector"

    def follow(self):
        self.click((By.ID, "redirect"))
        self.wait_for_url("/status_codes")
        return self.driver.current_url


class DownloadPage(BasePage):
    URL = BASE + "/download"

    def file_links(self):
        return [a.get_attribute("href") for a in self.find_all((By.CSS_SELECTOR, "#content .example a"))]


class AbTestPage(BasePage):
    URL = BASE + "/abtest"

    def heading(self):
        return self.text((By.TAG_NAME, "h3"))


class ForgotPasswordPage(BasePage):
    URL = BASE + "/forgot_password"

    def submit(self, email):
        self.type((By.ID, "email"), email)
        self.click((By.ID, "form_submit"))
        # the form posts and a new page loads: wait for it instead of reading the old body mid-navigation
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "e-mail"))
        return self.text((By.TAG_NAME, "body"))


class JsErrorPage(BasePage):
    URL = BASE + "/javascript_error"
