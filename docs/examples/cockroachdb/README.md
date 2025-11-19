# Memori CockroachDB Example

**Memori + CockroachDB** brings durable, distributed memory to AI — instantly, globally, and at any scale. Memori transforms conversations into structured, queryable intelligence, while CockroachDB keeps that memory available, resilient, and consistently accurate across regions. Deploy and scale effortlessly from prototype to production with zero downtime on enterprise-grade infrastructure. Give your AI a foundation to remember, reason, and evolve — with the simplicity of cloud and the reliability and power of distributed SQL.

Sign up for [CockroachDB Cloud](https://www.cockroachlabs.com/product/cloud/).

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   export COCKROACH_CONNECTION_STRING=postgresql://user:password@host:26257/defaultdb?sslmode=require
   ```

3. **Run the example**:
   ```bash
   uv run python main.py
   ```

## Full Example Using CockroachDB, SQLAlchemy and OpenAI

```python
from memori import Memori
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://dbuser:dbpassword@dbhost/dbname?sslmode=verify-full")
db_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = OpenAI()

mem = Memori(conn=db_session_factory).openai.register(client)
mem.attribution(entity_id="user_123", process_id="astronomer_agent")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What color is Mars?"}]
)

# The planet Mars is red.
print(response.choices[0].message.content)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "That planet we are talking about, in order from the sun, which one is it?"
        }
    ]
)

# Mars is the 4th planet from the sun.
print(response.choices[0].message.content)
```
