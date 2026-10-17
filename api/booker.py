"""Small client for Restful-Booker (https://restful-booker.herokuapp.com), a public practice API."""
import requests

BASE = "https://restful-booker.herokuapp.com"
ADMIN = {"username": "admin", "password": "password123"}  # documented demo credentials


class BookerClient:
    def __init__(self, base=BASE):
        self.base = base
        self.s = requests.Session()
        self.s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _url(self, path):
        return f"{self.base}{path}"

    def token(self, username=ADMIN["username"], password=ADMIN["password"]):
        return self.s.post(self._url("/auth"), json={"username": username, "password": password}, timeout=20)

    def list(self, **filters):
        return self.s.get(self._url("/booking"), params=filters, timeout=20)

    def get(self, booking_id):
        return self.s.get(self._url(f"/booking/{booking_id}"), timeout=20)

    def create(self, booking):
        return self.s.post(self._url("/booking"), json=booking, timeout=20)

    def update(self, booking_id, booking, token=None):
        return self.s.put(self._url(f"/booking/{booking_id}"), json=booking, timeout=20, **self._auth(token))

    def patch(self, booking_id, fields, token=None):
        return self.s.patch(self._url(f"/booking/{booking_id}"), json=fields, timeout=20, **self._auth(token))

    def delete(self, booking_id, token=None):
        return self.s.delete(self._url(f"/booking/{booking_id}"), timeout=20, **self._auth(token))

    @staticmethod
    def _auth(token):
        return {"cookies": {"token": token}} if token else {}
