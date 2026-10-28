# Selenium + pytest test automation framework

[![tests](https://github.com/MilosG997/selenium-pytest-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/MilosG997/selenium-pytest-framework/actions/workflows/tests.yml)

A UI and API test framework written from scratch in Python: **Selenium WebDriver + pytest**, Page Object Model, data-driven tests, parallel runs, HTML reports with screenshots and CI on every push. The suites run against public demo applications that exist for test practice:

| Suite | Application | Tests | What it shows |
|---|---|---|---|
| [`tests/ui/saucedemo`](tests/ui/saucedemo) | [SauceDemo](https://www.saucedemo.com) shop | 53 | Login rules, sorting, cart, checkout validation, order totals and tax, full purchase, state after reload and re-login, menu and footer links, protected pages, slow user, known bugs |
| [`tests/ui/internet`](tests/ui/internet) | [The Internet](https://the-internet.herokuapp.com) | 55 | Explicit waits, JS alerts, iframes and an editor inside one, new windows, shadow DOM, infinite scroll, sliders, modals, unstable ids, a 2,500-cell table, geolocation emulation, console errors, drag-and-drop, upload, keyboard |
| [`tests/ui/automationexercise`](tests/ui/automationexercise) | [Automation Exercise](https://automationexercise.com) shop | 28 | Register and delete account, login/logout, search, categories, brands, quantities, cart, reviews, contact form with file upload, UI checked against the API |
| [`tests/api`](tests/api) | [Restful-Booker](https://restful-booker.herokuapp.com) | 22 | Token auth, create/read/update/patch/delete, JSON Schema validation, filters, malformed JSON, 403/404 negative cases, cleanup |
| [`tests/api`](tests/api) | [Automation Exercise API](https://automationexercise.com/api_list) | 14 | Catalog schema, search, error responses, full account lifecycle (create, verify, read, update, delete) |
| [`tests/api`](tests/api) | [The Internet](https://the-internet.herokuapp.com) over HTTP | 9 | Basic and Digest auth, wrong password, status codes, 302 redirect, file download |

**181 tests**, about 5 minutes in parallel. 7 of them document real defects in the demo apps (see *Known bugs* below).

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
  automationexercise/     shop pages; ads blocked in the browser, JS-click fallback for overlays
api/booker.py             requests.Session client for the booking API
api/automationexercise.py client for the shop API + throwaway test identities
data/                     test data (JSON) and the booking JSON Schema
tests/
  conftest.py             --browser / --headed options
  ui/conftest.py          driver fixture + screenshot and URL attached to the HTML report on failure
  ui/saucedemo/           login, inventory, cart & checkout, navigation and state
  ui/internet/            widgets, plus shadow DOM, scrolling, modals, geolocation
  ui/automationexercise/  account, contact form, shop
  api/                    booking API, shop API, HTTP auth and status codes
```

- **Page Object Model**: tests read like steps (`shop.add("Sauce Labs Backpack")`, `cart.checkout().fill(...)`), locators live in one place.
- **No `sleep()`**: every wait is a `WebDriverWait` on a real condition, and every navigation in a page object waits for the next page before returning it (no reading a page that is still loading).
- **Data-driven**: login and checkout error cases come from [`data/saucedemo.json`](data/saucedemo.json) through `pytest.mark.parametrize`.
- **Markers**: `smoke`, `regression`, `api`, `known_bug`.
- **Known bugs are tests too**: tests for real defects are marked `xfail(strict=True)`, so the suite stays green while the bug exists and turns red the day it is fixed:
  - SauceDemo `problem_user`: every product shows the same image; *Add to cart* does nothing on some products
  - SauceDemo `error_user`: the Last Name field ignores typing at checkout
  - SauceDemo `visual_user`: the catalog shows different prices than for `standard_user`
  - The Internet: two broken images
  - Automation Exercise API: always answers HTTP 200, the real status is hidden in the JSON body
  - Restful-Booker: a booking with missing fields crashes the server (500) instead of returning 400
- **Test data that cleans up after itself**: accounts use generated `@example.com` identities and are deleted in a `finally`/fixture teardown, also when a step fails.
- **UI vs API cross-checks**: catalog, search and brand pages are compared with what the API returns.
- **Browser features through DevTools**: geolocation is emulated and permissions granted with CDP commands; the shadow DOM is reached with `element.shadow_root`; JS errors are read from the browser log.
- **Ad blocking**: Chrome/Edge block ad networks through the DevTools protocol, so ads never cover buttons.
- **Cross-browser**: Chrome, Edge and Firefox through one option; drivers come from Selenium Manager. On CI, Chrome runs every suite and Firefox runs SauceDemo and The Internet (Automation Exercise is full of ads that only Chrome can block through DevTools).
- **Live demo apps are flaky by nature**: on CI a failed test is retried twice (`pytest-rerunfailures`) before it counts, and every real failure is shown as a GitHub annotation on the run page.
- **CI**: GitHub Actions runs the UI suite on Chrome and Firefox in parallel plus the API suite on every push and pull request (pinned Ubuntu 24.04 runner), and uploads the HTML reports as artifacts. *Run workflow* in the Actions tab starts it by hand.

## Real-world use

The same approach tests my own client work in [qa-automation](https://github.com/MilosG997/qa-automation): a live Shopify store, an Android web app, a local business site and my own site.

---

[Mechanically Gifted](https://mechanicallygifted.rs) · Shopify development, websites and QA automation
