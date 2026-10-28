"""Automation Exercise: catalog, search, categories, brands, product page and cart."""
import pytest

from api.automationexercise import AEClient
from pages.automationexercise.pages import CartPage, HomePage, ProductsPage

# One worker for this shop: four parallel browsers hitting it at once is what triggers its bot protection
pytestmark = [pytest.mark.xdist_group("automationexercise")]


@pytest.fixture
def products(driver):
    return ProductsPage(driver).open()


@pytest.mark.smoke
def test_catalog_matches_the_api(products):
    """The products page and the products API must list the same items."""
    _, body = AEClient().products()
    assert sorted(products.ids()) == sorted(p["id"] for p in body["products"])


@pytest.mark.regression
@pytest.mark.parametrize("term", ["top", "jeans", "dress"])
def test_search_only_returns_matching_products(products, term):
    products.search(term)
    assert products.title() == "SEARCHED PRODUCTS"
    ids = products.ids()
    assert ids, f"no results for {term}"
    _, body = AEClient().search(term)
    assert sorted(ids) == sorted(p["id"] for p in body["products"]), "UI and API search must agree"


@pytest.mark.regression
def test_search_with_no_results(products):
    products.search("zzzz-no-such-product")
    assert products.names() == []


@pytest.mark.regression
@pytest.mark.parametrize("top, sub", [("Women", "Dress"), ("Women", "Tops"), ("Men", "Jeans"), ("Kids", "Dress")])
def test_category_page_title(products, top, sub):
    products.open_category(top, sub)
    assert products.title() == f"{top.upper()} - {sub.upper()} PRODUCTS"
    assert products.names()


@pytest.mark.regression
@pytest.mark.parametrize("brand", ["Polo", "H&M", "Madame", "Biba"])
def test_brand_page_lists_only_that_brand(products, brand):
    products.open_brand(brand)
    assert products.title() == f"BRAND - {brand.upper()} PRODUCTS"
    expected = {p["id"] for p in AEClient().products()[1]["products"] if p["brand"] == brand}
    assert set(products.ids()) == expected


@pytest.mark.regression
def test_product_detail_shows_all_info(products):
    detail = products.open_product(1)
    info = detail.info()
    assert info["name"] == "Blue Top"
    assert {"Category", "Availability", "Condition", "Brand"} <= info.keys()
    assert detail.price() == 500


@pytest.mark.smoke
def test_add_two_products_to_cart(products):
    products.add_to_cart(1)
    cart = products.add_to_cart(2, then_view_cart=True)
    rows = cart.rows()
    assert [r["id"] for r in rows] == ["1", "2"]
    for r in rows:
        assert r["quantity"] == 1
        assert r["total"] == r["price"]


@pytest.mark.regression
@pytest.mark.parametrize("quantity", [1, 4, 10])
def test_quantity_from_product_page(products, quantity):
    cart = products.open_product(3).add(quantity)
    row = cart.rows()[0]
    assert row["quantity"] == quantity
    assert row["total"] == row["price"] * quantity


@pytest.mark.regression
def test_remove_from_cart_until_empty(products):
    products.add_to_cart(1)
    cart = products.add_to_cart(5, then_view_cart=True)
    cart.remove("1")
    assert [r["id"] for r in cart.rows()] == ["5"]
    cart.remove("5")
    assert cart.is_empty()


@pytest.mark.regression
def test_write_a_review(products, user):
    message = products.open_product(2).review(user["name"], user["email"], "Fits well, automated review test.")
    assert message == "Thank you for your review."


@pytest.mark.regression
def test_footer_subscription(driver, user):
    assert HomePage(driver).open().subscribe(user["email"]) == "You have been successfully subscribed!"


@pytest.mark.regression
def test_cart_is_empty_for_a_new_visitor(driver):
    assert CartPage(driver).open().is_empty()
