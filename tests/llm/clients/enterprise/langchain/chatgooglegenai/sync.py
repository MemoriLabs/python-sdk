#!/usr/bin/env python3

import os

from database.core import TestDBSession
from langchain_google_genai import ChatGoogleGenerativeAI

from memori import Memori

if os.environ.get("GOOGLE_API_KEY", None) is None:
    raise RuntimeError("GOOGLE_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"

session = TestDBSession()
client = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

mem = Memori(conn=session).langchain.register(chatgooglegenai=client)

# Multiple registrations should not cause an issue.
mem.langchain.register(chatgooglegenai=client)

mem.attribution(parent_id="123", process_id="456")

print("-" * 25)

query = "What color is the planet Mars?"
print(f"me: {query}")

print("-" * 25)
print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

client.invoke(query)

print("-" * 25)
