#!/usr/bin/env python3

import os

from langchain_google_vertexai import ChatVertexAI

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None) is None:
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"

session = TestDBSession()
client = ChatVertexAI(
    model_name="gemini-2.0-flash",
    temperature=0,
    seed=42,
)

mem = Memori(conn=session).langchain.register(chatvertexai=client)

# Multiple registrations should not cause an issue.
mem.langchain.register(chatvertexai=client)

mem.attribution(parent_id="123", process_id="456")

print("-" * 25)

query = "What color is the planet Mars?"
print(f"me: {query}")

print("-" * 25)
print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

client.invoke(query)

print("-" * 25)
