#!/usr/bin/env python3

import asyncio
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from memori import Memori
from tests.database.core import TestDBSession

if os.environ.get("GEMINI_API_KEY", None) is None:
    raise RuntimeError("GEMINI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["MEMORI_API_KEY"] = "dev-no-such-key"


async def main():
    session = TestDBSession
    client = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", google_api_key=os.environ["GEMINI_API_KEY"]
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{question}"),
        ]
    )
    chain = prompt | client | StrOutputParser()

    mem = Memori(conn=session).langchain.register(chatgooglegenai=client)

    # Multiple registrations should not cause an issue.
    mem.langchain.register(chatgooglegenai=client)

    mem.attribution(entity_id="123", process_id="456")

    print("-" * 25)

    query = "What color is the planet Mars?"
    print(f"me: {query}")

    print("-" * 25)
    print("COLLECTOR PAYLOAD OCCURRED HERE!\n")

    async for _ in chain.astream({"question": query}):
        pass

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(main())
