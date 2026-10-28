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


def pytest_terminal_summary(terminalreporter, exitstatus):
    """On GitHub Actions, show every failure and error (setup, test, teardown or collection) as an annotation on the
    run page, so the reason is visible without opening the log."""
    if not os.environ.get("GITHUB_ACTIONS"):
        return
    shown = 0
    for kind in ("failed", "error"):
        for report in terminalreporter.stats.get(kind, []):
            lines = str(getattr(report, "longrepr", "") or kind).strip().splitlines()
            where = f'{getattr(report, "when", "collect")}: {getattr(report, "nodeid", "") or "collection"}'
            page = dict(getattr(report, "user_properties", [])).get("page", "")
            message = (lines[-1][:250] if lines else kind) + (f" | page: {page[:150]}" if page else "")
            terminalreporter.write_line(f"::error title={kind} in {where}::{message}")
            shown += 1
    if exitstatus and not shown:
        terminalreporter.write_line(f"::error title=pytest exit status {int(exitstatus)}::no test failed, see the log")
