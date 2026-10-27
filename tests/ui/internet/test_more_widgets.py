"""More tricky UI: shadow DOM, infinite scroll, sliders, iframes with an editor, modals, geolocation, unstable ids."""
import pytest
from selenium.webdriver.common.keys import Keys

from pages.internet.pages import (AbTestPage, ChallengingDomPage, DownloadPage, DynamicContentPage, EntryAdPage,
                                  FloatingMenuPage, ForgotPasswordPage, GeolocationPage, InfiniteScrollPage,
                                  JsErrorPage, LargeDomPage, NumberInputPage, RedirectorPage, ShadowDomPage,
                                  SliderPage, StatusCodesPage, TinyMcePage)

pytestmark = pytest.mark.regression


def _browser(driver):
    return driver.capabilities["browserName"].lower()


def test_shadow_dom_content_is_reachable(driver):
    page = ShadowDomPage(driver).open()
    assert page.slotted_texts()[0] == "Let's have some different text!"
    assert "In a list!" in page.slotted_texts()[1]
    assert page.slot_name() == "my-text"


def test_infinite_scroll_loads_more_blocks(driver):
    page = InfiniteScrollPage(driver).open()
    start = page.count()
    assert page.scroll_until(start + 3) >= start + 3


def test_floating_menu_stays_on_screen(driver):
    page = FloatingMenuPage(driver).open()
    page.scroll_to_bottom()
    assert page.find(page.MENU).is_displayed()
    assert 0 <= page.menu_top() < 200, "menu should follow the viewport"


@pytest.mark.parametrize("presses,expected", [(1, "0.5"), (3, "1.5"), (10, "5"), (20, "5")],
                         ids=["one_step", "three_steps", "to_max", "clamped_at_max"])
def test_slider_moves_with_arrow_keys(driver, presses, expected):
    assert SliderPage(driver).open().press(Keys.ARROW_RIGHT, presses) == expected


def test_number_input_arrow_keys(driver):
    page = NumberInputPage(driver).open()
    assert page.press(Keys.ARROW_UP, 3) == "3"
    assert page.press(Keys.ARROW_DOWN, 5) == "-2"


def test_number_input_ignores_letters(driver):
    assert NumberInputPage(driver).open().press("abc", 1) == ""


def test_challenging_dom_table_by_structure(driver):
    page = ChallengingDomPage(driver).open()
    assert page.headers() == ["Lorem", "Ipsum", "Dolor", "Sit", "Amet", "Diceret", "Action"]
    rows = page.rows()
    assert len(rows) == 10
    assert all(r[-1] == "edit delete" for r in rows)
    assert [r[0] for r in rows] == [f"Iuvaret{i}" for i in range(10)]


def test_large_dom_cell_lookup(driver):
    page = LargeDomPage(driver).open()
    assert page.table_size() == (50, 50)
    assert page.table_cell(1, 1) == "1.1"
    assert page.table_cell(50, 50) == "50.50"
    assert page.sibling(50, 3) == "50.3"
    assert page.sibling(1, 1) == "1.1"


def test_iframe_editor_content(driver):
    assert TinyMcePage(driver).open().editor_text() == "Your content goes here."


def test_entry_ad_modal_can_be_closed(driver):
    page = EntryAdPage(driver).open()
    assert page.is_visible(page.MODAL, timeout=5)
    page.close_ad()
    assert not page.find_all(page.MODAL)[0].is_displayed()


def test_geolocation_uses_the_emulated_position(driver):
    if _browser(driver) == "firefox":
        pytest.skip("geolocation override uses the Chrome DevTools protocol")
    driver.execute_cdp_cmd("Browser.grantPermissions", {"origin": "https://the-internet.herokuapp.com",
                                                        "permissions": ["geolocation"]})
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride",
                           {"latitude": 44.9417, "longitude": 20.2274, "accuracy": 10})  # Nova Pazova
    lat, lon = GeolocationPage(driver).open().where_am_i()
    assert (round(lat, 2), round(lon, 2)) == (44.94, 20.23)


def test_static_dynamic_content_survives_reload(driver):
    page = DynamicContentPage(driver).open()
    first = page.texts()[:2]
    driver.refresh()
    assert page.texts()[:2] == first


def test_status_code_links(driver):
    links = StatusCodesPage(driver).open().code_links()
    assert [l.rsplit("/", 1)[1] for l in links] == ["200", "301", "404", "500"]


def test_redirect_link_lands_on_status_codes(driver):
    assert RedirectorPage(driver).open().follow().endswith("/status_codes")


def test_download_page_lists_files(driver):
    links = DownloadPage(driver).open().file_links()
    assert len(links) >= 1
    assert all("/download/" in l for l in links)


def test_ab_test_shows_a_known_variant(driver):
    assert AbTestPage(driver).open().heading() in {"A/B Test Control", "A/B Test Variation 1", "No A/B Test"}


def test_forgot_password_confirms(driver):
    assert "Your e-mail's been sent!" in ForgotPasswordPage(driver).open().submit("qa-probe@example.com")


def test_javascript_error_is_caught_in_the_console(driver):
    if _browser(driver) == "firefox":
        pytest.skip("browser console logs are only exposed by Chromium drivers")
    JsErrorPage(driver).open()
    errors = [l["message"] for l in driver.get_log("browser") if l["level"] == "SEVERE"]
    assert any("Cannot read properties of undefined" in e for e in errors)
