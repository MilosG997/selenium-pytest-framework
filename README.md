# Selenium + pytest test automation framework

[![tests](https://github.com/MilosG997/selenium-pytest-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/MilosG997/selenium-pytest-framework/actions/workflows/tests.yml)

A UI and API test framework written from scratch in Python: **Selenium WebDriver + pytest**, Page Object Model, data-driven tests, parallel runs, HTML reports with screenshots and CI on every push. The suites run against public demo applications that exist for test practice:

| Suite | Application | Tests | What it shows |
|---|---|---|---|
| [`tests/ui/saucedemo`](tests/ui/saucedemo) | [SauceDemo](https://www.saucedemo.com) shop | 32 | Login rules, catalog sorting, cart, checkout validation, order totals and tax, full purchase, known bugs |
| [`tests/ui/internet`](tests/ui/internet) | [The Internet](https://the-internet.herokuapp.com) | 34 | Explicit waits, JS alerts, nested iframes, new windows, hover and right click, HTML5 drag-and-drop, file upload, sortable tables, keyboard |
| [`tests/api`](tests/api) | [Restful-Booker](https://restful-booker.herokuapp.com) | 12 | Token auth, create/read/update/patch/delete, JSON Schema validation, 403/404 negative cases, cleanup |

## Run it

```bash
pip install -r requirements.txt

pytest                                   # everything, headless Chrome
pytest -n auto                           # in parallel
pytest -m smoke                          # critical path only (~1 min)
pytest tests/api                         # API only, no browser
pytest --browser edge                    # or firefox
pytest --headed -k checkout              # watch one area run
pytest --html=reports/report.html --self-contained-html
```

## How it is built

```
pages/
  base_page.py            explicit waits, click/type/text helpers, data-test locators
  saucedemo/pages.py      LoginPage, InventoryPage, ProductPage, CartPage, Checkout pages
  internet/pages.py       one small page object per widget
api/booker.py             requests.Session client for the booking API
data/                     test data (JSON) and the booking JSON Schema
tests/
  conftest.py             --browser / --headed options
  ui/conftest.py          driver fixture + screenshot and URL attached to the HTML report on failure
  ui/saucedemo/           login, inventory, cart & checkout
  ui/internet/            widgets
  api/                    booking API
```

- **Page Object Model**: tests read like steps (`shop.add("Sauce Labs Backpack")`, `cart.checkout().fill(...)`), locators live in one place.
- **No `sleep()`**: every wait is a `WebDriverWait` on a real condition.
- **Data-driven**: login and checkout error cases come from [`data/saucedemo.json`](data/saucedemo.json) through `pytest.mark.parametrize`.
- **Markers**: `smoke`, `regression`, `api`, `known_bug`.
- **Known bugs are tests too**: SauceDemo's `problem_user` and `error_user` and the broken images page have real defects. Those tests are marked `xfail(strict=True)`, so the suite stays green while the bug exists and turns red the day it is fixed.
- **Fixtures with cleanup**: API tests create their own booking and delete it afterwards, even when an assertion fails.
- **Cross-browser**: Chrome, Edge and Firefox through one option; drivers come from Selenium Manager.
- **CI**: GitHub Actions runs the UI suite on Chrome and Firefox in parallel plus the API suite, on every push and every Monday, and uploads the HTML reports as artifacts.

## Real-world use

The same approach tests my own client work in [qa-automation](https://github.com/MilosG997/qa-automation): a live Shopify store, a web app and my business site.

---

[Mechanically Gifted](https://mechanicallygifted.rs) · Shopify development, websites and QA automation
