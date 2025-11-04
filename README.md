[![Memori Labs](https://s3.us-east-1.amazonaws.com/images.memorilabs.ai/banner.png)](https://memorilabs.ai/)

<p align="center">
  <strong>An open-source SQL-Native memory engine for AI</strong>
</p>

<p align="center">
  <i>From Postgres to MySQL, Memori plugs into the SQL databases you already use. Simple setup, infinite scale without new infrastructure.</i>
</p>

<p align="center">
  <a href="https://memorilabs.ai/">Learn more</a>
  ·
  <a href="https://www.gibsonai.com/discord">Join Discord</a>
</p>

<p align="center">
  <a href="https://badge.fury.io/py/memorisdk">
    <img src="https://badge.fury.io/py/memori.svg" alt="PyPI version">
  </a>
  <a href="https://pepy.tech/projects/memorisdk">
    <img src="https://static.pepy.tech/badge/memorisdk" alt="Downloads">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  </a>
</p>

---

## Getting Started

Install Memori:

```bash
pip install memori
```

## Example with OpenAI

```python
from openai import OpenAI
from memori import Memori

client = OpenAI(...)
mem = Memori().openai.register(client)
```

## Attribution

```python
mem.attribution(parent_id="12345", process_id="my-ai-bot")
```

## Session Management

```python
mem.new_session()
```

or

```python
session_id = mem.config.session_id

# ...

mem.set_session(session_id)
```

## Configure Your Database

1. Run this command once, via CI/CD or anytime you update Memori.

    ```python
    Memori(conn=session).config.storage.build()
    ```

2. Instantiate Memori with the connection.

    ```python
    from openai import OpenAI
    from memori import Memori

    client = OpenAI(...)
    mem = Memori(conn=session).openai.register(client)
    ```

## Full Example Using MySQL, SQLAlchemy and OpenAI

```python
from memori import Memori
from MyLoggedInUser import MyLoggedInUser
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = create_engine("mysql+pymysql://dbuser:dbpassword@dbhost/dbname")
session = sessionmaker(autocommit=False, autoflush=False, bind=db)()

client = OpenAI()

mem = Memori(conn=session).openai.register(client)
mem.attribution(parent_id=str(MyLoggedInUser.id), process_id="astronomer_agent")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role", "user", "content": "What color is Mars?"}]
)

# The planet Mars is red.
print(response.choices[0].message.content)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role", "user",
            "content": "That planet we are talking about, in order from the sun, which one is it?"
        }
    ]
)

# Mars is the 4th planet from the sun.
print(response.choices[0].message.content)
```

## Supported LLM

- OpenAI
- Gemini
- Anthropic
- Bedrock
- Grok (xAI)

_(unstreamed, streamed, synchronous and asynchronous)_

## Supported Frameworks

- LangChain
- Pydantic AI

## Supported Database Integrations

- **DB API 2.0** - Direct support for any Python database driver that implements the [PEP 249 Database API Specification v2.0](https://peps.python.org/pep-0249/). This includes drivers like `psycopg`, `pymysql`, `MySQLdb`, and `sqlite3`. Simply pass your raw database connection object to Memori and it will automatically detect and use the appropriate dialect.
- **Django** - Native integration with Django's ORM and database layer
- SQLAlchemy

## Supported Datastores

- CockroachDB
- MariaDB
- MongoDB
- MySQL
- Neon
- PostgreSQL
- SQLite
- Supabase

## Memori Advanced Augmentation

Memories are tracked at several different levels:

- parent: think person, place, or thing; like a user
- process: think your agent, LLM interaction or program
- session: the current interactions between the parent, process and the LLM

Memori's Advanced Augmentation enhances memories at each of these levels with:

- attributes
- events
- facts
- people
- preferences
- relationships
- rules
- skills

Memori knows who your user is, what tasks your agent handles and creates unparalleled context between the two. Augmentation occurs in the background incurring no latency.

By default, Memori Advanced Augmentation is available without an account but rate limited. When you need increased limited, [sign up for Memori Advanced Augmentation](https://memorilabs.ai/sign-up/github) or execute the following:

```bash
python3 -m memori sign-up <email_address>
```

Memori Advanced Augmentation is always free for developers!

Once you've obtained an API key, simply set the following environment variable:

```bash
export MEMORI_API_KEY=[api_key]
```

## Running Memori Advanced Augmentation

The process of augmenting memories is technically complex and requires time for processing. Your application should benefit from the power of augmentation without the latency. In order to achieve this we have designed a background job that you need to run in order to activate Advanced Augmentation.

We designed this job for scale and parallel processing and suggest that you run the job in a loop as fast you want. The benefit of running this job frequently is that memories can be formed in near real time which means additional context will be available immediately. However, if it's more suitable for you to run augmentation once a day you can do that as well.

Note, that this job is for augmenting memories, not for recalling them. It is imperative that recall be done in real time at the moment your system is engaging the LLM. Recall will execute at exactly the right moment but relies on the enhancements made by Augmentation to be fully effective.

To execute Advanced Augmentation, execute the following:

```python
Memori(conn=session).augmentation.run()
```

Here is a full example for how Advanced Augmentation should be run:

```python
#!/usr/bin/env python3

import os
import sys
import time

from memori import Memori

if len(sys.argv) != 2:
    print(f"usage: {os.path.basename(sys.argv[0])} [int(job_id)]")
    exit(1)

Memori.augmentation.pidlock(dir="/tmp")

def main():
    job_id = sys.argv[1]
    seconds_sleep = 1
    session = [however you connect to your datastore]
    with_output = True

    mem = Memori(conn=session)

    while True:
        mem.augmentation.run(job_id=job_id, with_output=with_output)
        time.sleep(seconds_sleep)

if __name__ == "__main__":
    main()
```
