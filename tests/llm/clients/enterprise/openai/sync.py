#!/usr/bin/env python3

import os

from database.core import TestDBSession
from openai import OpenAI

from memori import Memori

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"

session = TestDBSession()
client = OpenAI()

mem = Memori(conn=session).openai.register(client)

# Multiple registrations should not cause an issue.
mem.openai.register(client)

mem.attribution(parent_id="123", process_id="456")

print("-" * 25)

query = "What color is the planet Mars?"
print(f"me: {query}")

print("-" * 25)
print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": query}],
)

print("-" * 25)
