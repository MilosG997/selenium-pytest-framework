import warnings

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
    for attempt in range(3):  # cleanup must not turn a passed test red: retry a hiccup of the public API
        try:
            api.delete_account(user["email"], user["password"])
            break
        except Exception:
            if attempt == 2:
                warnings.warn(f'could not delete test account {user["email"]}')
