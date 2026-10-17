import pytest

from api.automationexercise import AEClient, fake_user


@pytest.fixture
def user():
    """A fresh throwaway identity (not registered yet)."""
    return fake_user()


@pytest.fixture
def registered_user(user):
    """Registered through the API for speed; always deleted afterwards."""
    api = AEClient()
    _, body = api.create_account(user)
    assert body.get("responseCode") == 201, body
    yield user
    api.delete_account(user["email"], user["password"])
