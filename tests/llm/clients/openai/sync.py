#!/usr/bin/env python3

import os
import pprint

from database.core import TestDBSession
from openai import OpenAI

from memori import Memori

if os.environ.get("MEMORI_TEST_MODE", None) != "1":
    raise RuntimeError("MEMORI_TEST_MODE is not set")

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")

session = TestDBSession()
client = OpenAI()

mem = Memori(conn=session).openai.register(client)

# Multiple registrations should not cause an issue.
mem.openai.register(client)

mem.attribution(parent_id="123", process_id="456")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What color is the planet Mars?"}],
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "That planet we're talking about, in order from the sun which one is it?",
        }
    ],
)

print(response)
