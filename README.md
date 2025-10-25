[![Memori Labs](https://s3.us-east-1.amazonaws.com/images.memorilabs.ai/banner.png)](https://memorilabs.ai/)

# memori

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
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
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
    Memori(conn=session).storage.build()
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

db = create_engine("mysql+pymysql://dbuser:dbuser@dbhost/dbname")
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

_(unstreamed, streamed, synchronous and asynchronous)_

## Supported Frameworks

- LangChain
- Pydantic AI

## Supported Datastores

- CockroachDB
- MariaDB
- MongoDB
- MySQL
- Neon
- PostgreSQL
- SQLite
- Supabase

## Advanced Augmentation

Memories are tracked at several different levels:

- parent: think person, place, or thing; like a user
- process: think your agent, LLM interaction or program
- session: the current interactions between the parent, process and the LLM

Memori's advanced augmentation enhances memories at each of these levels with:

- attributes
- facts
- preferences
- skills
- rules
- events

Matching these enhancements against those of the process, Memori delivers unparalleled context.
