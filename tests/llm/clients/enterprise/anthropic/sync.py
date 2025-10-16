#!/usr/bin/env python3

import os

import anthropic
from database.core import TestDBSession

from memori import Memori

if os.environ.get("ANTHROPIC_API_KEY", None) is None:
    raise RuntimeError("ANTHROPIC_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"

session = TestDBSession()
client = anthropic.Anthropic()

mem = Memori(conn=session).anthropic.register(client)

# Multiple registrations should not cause an issue.
mem.anthropic.register(client)

mem.attribution(parent_id="123", process_id="456")

print("-" * 25)

query = "What color is the planet Mars?"
print(f"me: {query}")

print("-" * 25)
print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": query}],
)

print("-" * 25)
