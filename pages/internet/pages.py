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
