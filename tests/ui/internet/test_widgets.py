"""Tricky UI widgets: waits, alerts, frames, windows, mouse actions, uploads, tables."""
import pytest
from selenium.webdriver.common.keys import Keys

from pages.internet.pages import (AddRemovePage, AlertsPage, BrokenImagesPage, CheckboxesPage, ContextMenuPage,
                                  DragAndDropPage, DropdownPage, DynamicControlsPage, DynamicLoadingPage,
                                  HoversPage, KeyPressesPage, LoginFormPage, NestedFramesPage, TablesPage,
                                  UploadPage, WindowsPage)

pytestmark = pytest.mark.regression


def test_checkboxes_toggle(driver):
    page = CheckboxesPage(driver).open()
    before = page.states()
    page.toggle(0)
    page.toggle(1)
    assert page.states() == [not s for s in before]


@pytest.mark.parametrize("option", ["Option 1", "Option 2"])
def test_dropdown_selection(driver, option):
    page = DropdownPage(driver).open()
    page.choose(option)
    assert page.selected() == option


@pytest.mark.smoke
@pytest.mark.parametrize("example", [1, 2], ids=["hidden_in_dom", "rendered_after_load"])
def test_dynamic_loading_with_explicit_wait(driver, example):
    assert DynamicLoadingPage(driver).open_example(example).start_and_wait() == "Hello World!"


def test_dynamic_controls(driver):
    page = DynamicControlsPage(driver).open()
    assert page.remove_checkbox() == "It's gone!"
    assert page.enable_input() == "It's enabled!"
    page.type(page.INPUT, "typed after enable")
    assert page.find(page.INPUT).get_attribute("value") == "typed after enable"


def test_js_alert(driver):
    assert AlertsPage(driver).open().js_alert() == "You successfully clicked an alert"


@pytest.mark.parametrize("accept, expected", [(True, "You clicked: Ok"), (False, "You clicked: Cancel")])
def test_js_confirm(driver, accept, expected):
    assert AlertsPage(driver).open().js_confirm(accept) == expected


def test_js_prompt(driver):
    assert AlertsPage(driver).open().js_prompt("Mechanically Gifted") == "You entered: Mechanically Gifted"


def test_new_window_and_switch_back(driver):
    page = WindowsPage(driver).open()
    original, heading = page.open_new_window()
    assert heading == "New Window"
    driver.close()
    driver.switch_to.window(original)
    assert page.text(("tag name", "h3")) == "Opening a new window"


@pytest.mark.parametrize("path, expected", [
    (("frame-top", "frame-left"), "LEFT"),
    (("frame-top", "frame-middle"), "MIDDLE"),
    (("frame-top", "frame-right"), "RIGHT"),
    (("frame-bottom",), "BOTTOM"),
])
def test_nested_frames(driver, path, expected):
    assert NestedFramesPage(driver).open().frame_text(*path) == expected


@pytest.mark.parametrize("index", [0, 1, 2])
def test_hover_reveals_user_name(driver, index):
    assert HoversPage(driver).open().hover_caption(index) == f"name: user{index + 1}"


def test_html5_drag_and_drop(driver):
    page = DragAndDropPage(driver).open()
    assert page.order() == ["A", "B"]
    page.drag("column-a", "column-b")
    assert page.order() == ["B", "A"]


def test_file_upload(driver, tmp_path):
    file = tmp_path / "qa-upload-check.txt"
    file.write_text("uploaded by selenium")
    assert UploadPage(driver).open().upload(file.resolve()) == file.name


@pytest.mark.parametrize("header", ["Last Name", "First Name", "Email"])
def test_table_sorts_by_column(driver, header):
    page = TablesPage(driver).open()
    page.sort_by(header)
    values = page.column(header)
    assert values == sorted(values)


def test_table_amounts_are_money(driver):
    dues = TablesPage(driver).open().column("Due")
    assert all(d.startswith("$") and float(d[1:]) >= 0 for d in dues)


def test_add_and_remove_elements(driver):
    page = AddRemovePage(driver).open()
    page.add(3)
    page.delete_one()
    assert page.count() == 2


@pytest.mark.smoke
def test_login_form_success_and_logout(driver):
    page = LoginFormPage(driver).open()
    assert "You logged into a secure area!" in page.login(page.USER, page.PASSWORD)
    assert "You logged out of the secure area!" in page.logout()


@pytest.mark.parametrize("username, password, message", [
    ("tomsmith", "wrong", "Your password is invalid!"),
    ("nobody", "SuperSecretPassword!", "Your username is invalid!"),
], ids=["wrong_password", "wrong_username"])
def test_login_form_errors(driver, username, password, message):
    assert message in LoginFormPage(driver).open().login(username, password)


@pytest.mark.parametrize("key, name", [(Keys.TAB, "TAB"), (Keys.ESCAPE, "ESCAPE"), ("q", "Q")], ids=["tab", "escape", "letter"])
def test_key_presses(driver, key, name):
    assert KeyPressesPage(driver).open().press(key) == f"You entered: {name}"


def test_right_click_context_menu(driver):
    assert ContextMenuPage(driver).open().right_click_box() == "You selected a context menu"


def test_broken_image_detector_finds_them(driver):
    """The page has two broken images on purpose; the detector must find exactly those."""
    assert sorted(BrokenImagesPage(driver).open().broken()) == ["asdf.jpg", "hjkl.jpg"]


@pytest.mark.known_bug
@pytest.mark.xfail(strict=True, reason="the page ships two broken images")
def test_all_images_load(driver):
    assert BrokenImagesPage(driver).open().broken() == []
