import pytest


@pytest.mark.smoke
def test_catalog_lists_all_products(shop, data):
    assert sorted(shop.names()) == sorted(data["products"])
    assert all(price > 0 for price in shop.prices())


@pytest.mark.regression
@pytest.mark.parametrize("order, key, reverse", [
    ("az", "names", False), ("za", "names", True),
    ("lohi", "prices", False), ("hilo", "prices", True),
], ids=["name_a_to_z", "name_z_to_a", "price_low_to_high", "price_high_to_low"])
def test_sorting(shop, order, key, reverse):
    shop.sort_by(order)
    values = getattr(shop, key)()
    assert values == sorted(values, reverse=reverse)


@pytest.mark.smoke
def test_add_and_remove_updates_cart_badge(shop):
    shop.add("Sauce Labs Backpack")
    shop.add("Sauce Labs Bike Light")
    assert shop.cart_count() == 2
    assert shop.button_text("Sauce Labs Backpack") == "Remove"
    shop.remove("Sauce Labs Backpack")
    assert shop.cart_count() == 1
    assert shop.button_text("Sauce Labs Backpack") == "Add to cart"


@pytest.mark.regression
def test_product_details_match_catalog(shop):
    shop.sort_by("hilo")
    name, price = shop.names()[0], shop.prices()[0]
    product = shop.open_product(name)
    assert product.name() == name
    assert product.price() == price
    product.add()
    assert product.cart_count() == 1
    assert product.back().is_open()


@pytest.mark.regression
def test_reset_app_state_empties_the_cart(shop):
    shop.add("Sauce Labs Onesie")
    assert shop.cart_count() == 1
    shop.reset_app_state()
    assert shop.cart_count() == 0


@pytest.mark.known_bug
@pytest.mark.xfail(strict=True, reason="problem_user: every product shows the same image")
def test_problem_user_sees_a_different_image_for_each_product(login_as):
    inventory = login_as("problem_user")
    sources = inventory.image_sources()
    assert len(set(sources)) == len(sources)


@pytest.mark.known_bug
@pytest.mark.xfail(strict=True, reason="problem_user: 'Add to cart' does nothing on some products")
def test_problem_user_can_add_every_product(login_as, data):
    inventory = login_as("problem_user")
    for name in data["products"]:
        inventory.add(name)
    assert inventory.cart_count() == len(data["products"])
