"""Command-line options shared by all suites.

    pytest --browser edge         Chrome (default), Edge or Firefox
    pytest --headed               show the browser window
    pytest -m smoke               only the critical path
    pytest -n auto                run in parallel (pytest-xdist)
    pytest --html=reports/report.html --self-contained-html
"""


def pytest_addoption(parser):
    parser.addoption("--browser", default="chrome", choices=["chrome", "edge", "firefox"])
    parser.addoption("--headed", action="store_true", help="show the browser window")


def pytest_html_report_title(report):
    report.title = "Selenium + pytest framework: test report"
