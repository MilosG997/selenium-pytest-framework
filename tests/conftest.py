"""Command-line options shared by all suites.

    pytest --browser edge         Chrome (default), Edge or Firefox
    pytest --headed               show the browser window
    pytest -m smoke               only the critical path
    pytest -n auto                run in parallel (pytest-xdist)
    pytest --html=reports/report.html --self-contained-html
"""
import os


def pytest_addoption(parser):
    parser.addoption("--browser", default="chrome", choices=["chrome", "edge", "firefox"])
    parser.addoption("--headed", action="store_true", help="show the browser window")


def pytest_html_report_title(report):
    report.title = "Selenium + pytest framework: test report"


_terminal = None


def pytest_configure(config):
    global _terminal
    _terminal = config.pluginmanager.get_plugin("terminalreporter")


def pytest_runtest_logreport(report):
    """On GitHub Actions, show every failure as an annotation on the run page (no need to open the log)."""
    if os.environ.get("GITHUB_ACTIONS") and _terminal and report.failed and report.when in ("setup", "call"):
        message = str(report.longrepr).strip().splitlines()[-1][:300]
        _terminal.write_line(f"::error title={report.nodeid}::{message}")
