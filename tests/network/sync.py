#!/usr/bin/env python3

import pprint

from requests.exceptions import HTTPError

from memori._config import Config
from memori._network import AsyncRequest

config = Config()

request = AsyncRequest(config)

print("-" * 25)

try:
    r = request.get("https://api.gibsonai.com/")
    raise RuntimeError("HTTPError was not thrown when expected")
except HTTPError as e:
    assert e.response.status_code == 404

print("404 EXCEPTION HANDLED CORRECTLY")
print("-" * 25)
print("GIBSONAI BOOTSTRAP SHOULD APPEAR BELOW!\n")

r = request.get(
    "https://api.gibsonai.com/v1/bootstrap",
    headers={"X-Gibson-Client-ID": "da287371-240b-4b53-bfde-4b1581cca62a"},
)
pprint.pprint(r.json())

print("-" * 25)
