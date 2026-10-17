"""Client for the Automation Exercise public API (https://automationexercise.com/api_list).

Note: this API answers HTTP 200 for everything and puts the real status in the JSON body
("responseCode"). The client returns both so tests can check each one.
"""
import uuid

import requests

BASE = "https://automationexercise.com/api"


def fake_user():
    """A throwaway test identity on example.com (never a real person); tests delete it afterwards."""
    tag = uuid.uuid4().hex[:10]
    return {"name": "QA Bot", "email": f"qa-bot-{tag}@example.com", "password": f"Qa!{tag}",
            "title": "Mr", "birth": ("10", "5", "1995"), "first_name": "QA", "last_name": "Bot",
            "company": "Test Co", "address": "1 Test Street", "country": "Canada", "state": "Ontario",
            "city": "Toronto", "zipcode": "M5V 2T6", "mobile_number": "+15550100"}


class AEClient:
    def __init__(self):
        self.s = requests.Session()

    def call(self, method, path, **kw):
        r = self.s.request(method, f"{BASE}/{path}", timeout=30, **kw)
        try:
            body = r.json()
        except ValueError:
            body = {}
        return r.status_code, body

    def products(self):
        return self.call("GET", "productsList")

    def brands(self):
        return self.call("GET", "brandsList")

    def search(self, term=None):
        return self.call("POST", "searchProduct", data={"search_product": term} if term is not None else {})

    def verify_login(self, email=None, password=None):
        data = {k: v for k, v in (("email", email), ("password", password)) if v is not None}
        return self.call("POST", "verifyLogin", data=data)

    @staticmethod
    def _account_form(u):
        return {"name": u["name"], "email": u["email"], "password": u["password"], "title": u["title"],
                "birth_date": u["birth"][0], "birth_month": u["birth"][1], "birth_year": u["birth"][2],
                "firstname": u["first_name"], "lastname": u["last_name"], "company": u["company"],
                "address1": u["address"], "address2": "", "country": u["country"], "zipcode": u["zipcode"],
                "state": u["state"], "city": u["city"], "mobile_number": u["mobile_number"]}

    def create_account(self, user):
        return self.call("POST", "createAccount", data=self._account_form(user))

    def update_account(self, user):
        return self.call("PUT", "updateAccount", data=self._account_form(user))

    def user_detail(self, email):
        return self.call("GET", "getUserDetailByEmail", params={"email": email})

    def delete_account(self, email, password):
        return self.call("DELETE", "deleteAccount", data={"email": email, "password": password})
