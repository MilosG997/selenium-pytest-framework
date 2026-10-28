"""Automation Exercise: register, login, logout, delete account, contact form with file upload."""
import pytest

from api.automationexercise import AEClient
from pages.automationexercise.pages import ContactPage, LoginSignupPage, SignupPage

# One worker for this shop: four parallel browsers hitting it at once is what triggers its bot protection
pytestmark = [pytest.mark.xdist_group("automationexercise")]


@pytest.mark.smoke
def test_register_through_the_ui_then_delete(driver, user):
    signup = LoginSignupPage(driver).open().start_signup(user["name"], user["email"])
    try:
        assert signup.fill_and_create(user) == "ACCOUNT CREATED!"
        home = signup.continue_()
        assert home.logged_in_as() == user["name"]
        home.click(home.DELETE_ACCOUNT)
        assert SignupPage(driver).text(SignupPage.DELETED).upper() == "ACCOUNT DELETED!"
    finally:
        AEClient().delete_account(user["email"], user["password"])  # no leftovers if a step failed


@pytest.mark.smoke
def test_login_and_logout(driver, registered_user):
    page = LoginSignupPage(driver).open()
    page.login(registered_user["email"], registered_user["password"])
    assert page.logged_in_as() == registered_user["name"]
    page.click(page.LOGOUT)
    page.wait_for_url("/login")
    assert not page.is_visible(page.LOGGED_IN_AS)


@pytest.mark.regression
@pytest.mark.parametrize("email, password", [
    ("nobody-qa@example.com", "whatever"),
    (None, "wrong-password"),
], ids=["unknown_email", "wrong_password"])
def test_login_errors(driver, registered_user, email, password):
    page = LoginSignupPage(driver).open()
    page.login(email or registered_user["email"], password)
    assert page.error() == "Your email or password is incorrect!"


@pytest.mark.regression
def test_signup_with_existing_email(driver, registered_user):
    page = LoginSignupPage(driver).open()
    page.start_signup("Someone Else", registered_user["email"])
    assert page.error() == "Email Address already exist!"


@pytest.mark.regression
def test_contact_form_with_attachment(driver, user, tmp_path):
    file = tmp_path / "bug-report.txt"
    file.write_text("Steps to reproduce: ...")
    message = ContactPage(driver).open().send(user["name"], user["email"], "Automated test",
                                              "Sent by the Selenium suite.", file.resolve())
    assert message == "Success! Your details have been submitted successfully."
