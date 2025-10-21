#!/usr/bin/env python3

import asyncio
import os
from typing import List

from database.core import TestDBSession
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from memori import Memori

if os.environ.get("GOOGLE_API_KEY", None) is None:
    raise RuntimeError("GOOGLE_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


class Color(BaseModel):
    color: str


session = TestDBSession()
client = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

mem = Memori(conn=session).langchain.register(chatgooglegenai=client)

# Multiple registrations should not cause an issue.
mem.langchain.register(chatgooglegenai=client)

mem.attribution(parent_id="123", process_id="456")

print("-" * 25)

query = "What color is the planet Mars: {color}"
print(f"me: {query}")

prompt = ChatPromptTemplate.from_messages([("user", query)])
chain = prompt | client.with_structured_output(Color)

print("-" * 25)
print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

chain.invoke({"color": "red"})

print("-" * 25)
