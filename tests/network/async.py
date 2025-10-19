#!/usr/bin/env python3

import asyncio
import pprint

from aiohttp.client_exceptions import ClientResponseError
from requests.exceptions import HTTPError

from memori._config import Config
from memori._network import AsyncRequest


async def run():
    config = Config()

    request = AsyncRequest(config)

    print("-" * 25)

    try:
        r = await request.get("https://api.gibsonai.com/")
        raise RuntimeError("HTTPError was not thrown when expected")
    except ClientResponseError as e:
        assert e.status == 404

    print("404 EXCEPTION HANDLED CORRECTLY")
    print("-" * 25)
    print("GIBSONAI BOOTSTRAP SHOULD APPEAR BELOW!\n")

    r = await request.get(
        "https://api.gibsonai.com/v1/bootstrap",
        headers={"X-Gibson-Client-ID": "da287371-240b-4b53-bfde-4b1581cca62a"},
    )
    pprint.pprint(await r.json())

    print("-" * 25)


if __name__ == "__main__":
    asyncio.run(run())
