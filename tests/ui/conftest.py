"""Browser fixtures for UI tests: one clean browser per test, screenshot in the HTML report on failure."""
import base64

import pytest
from selenium import webdriver


def _options(name, headed):
    options = {"chrome": webdriver.ChromeOptions, "edge": webdriver.EdgeOptions,
               "firefox": webdriver.FirefoxOptions}[name]()
    if not headed:
        options.add_argument("--headless=new" if name != "firefox" else "-headless")
    if name != "firefox":
        options.add_argument("--window-size=1366,900")
        # SauceDemo uses a known-breached demo password; keep Chrome's password popups out of the way
        options.add_experimental_option("prefs", {"credentials_enable_service": False,
                                                  "profile.password_manager_enabled": False,
                                                  "profile.password_manager_leak_detection": False})
    return options


@pytest.fixture
def driver(request):
    name = request.config.getoption("--browser")
    headed = request.config.getoption("--headed")
    factory = {"chrome": webdriver.Chrome, "edge": webdriver.Edge, "firefox": webdriver.Firefox}[name]
    d = factory(options=_options(name, headed))
    if name == "firefox":
        d.set_window_size(1366, 900)
    d.set_page_load_timeout(45)
    yield d
    d.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    d = item.funcargs.get("driver")
    html = item.config.pluginmanager.getplugin("html")
    if d is None or html is None:
        return
    png = d.get_screenshot_as_png()
    extras = getattr(report, "extras", [])
    extras.append(html.extras.png(base64.b64encode(png).decode(), name="screenshot"))
    extras.append(html.extras.url(d.current_url, name="page at failure"))
    report.extras = extras
