"""HTTP-level checks on The Internet: auth schemes, status codes, redirects and downloads (requests, no browser)."""
import pytest
import requests
from requests.auth import HTTPDigestAuth

BASE = "https://the-internet.herokuapp.com"
pytestmark = pytest.mark.api


@pytest.mark.parametrize("path,auth_type", [("/basic_auth", None), ("/digest_auth", HTTPDigestAuth)])
def test_auth_required_and_accepted(path, auth_type):
    assert requests.get(BASE + path, timeout=20).status_code == 401
    auth = auth_type("admin", "admin") if auth_type else ("admin", "admin")  # demo credentials from the page
    response = requests.get(BASE + path, auth=auth, timeout=20)
    assert response.status_code == 200
    assert "Congratulations" in response.text


def test_basic_auth_rejects_wrong_password():
    assert requests.get(BASE + "/basic_auth", auth=("admin", "wrong"), timeout=20).status_code == 401


@pytest.mark.parametrize("code", [200, 301, 404, 500])
def test_status_code_pages_return_their_code(code):
    assert requests.get(f"{BASE}/status_codes/{code}", allow_redirects=False, timeout=20).status_code == code


def test_redirect_is_a_302_to_status_codes():
    response = requests.get(BASE + "/redirect", allow_redirects=False, timeout=20)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/status_codes")


def test_downloadable_file_is_served():
    response = requests.get(BASE + "/download/11.txt", timeout=20)
    assert response.status_code == 200
    assert "attachment" in response.headers.get("Content-Disposition", "") or response.headers.get("Content-Type")
