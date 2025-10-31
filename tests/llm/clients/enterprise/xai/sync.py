#!/usr/bin/env python3

import os

from xai_sdk import Client
from xai_sdk.chat import user

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("XAI_API_KEY", None) is None:
    raise RuntimeError("XAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"

session = TestDBSession()
client = Client(api_key=os.environ.get("XAI_API_KEY"))

mem = Memori(conn=session).xai.register(client)

mem.xai.register(client)

mem.attribution(parent_id="123", process_id="456")

print("-" * 25)

query = "What color is the planet Mars?"
print(f"me: {query}")

print("-" * 25)
print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

chat = client.chat.create(
    model="grok-4",
    messages=[user(query)],
)
response = chat.sample()

print("-" * 25)
