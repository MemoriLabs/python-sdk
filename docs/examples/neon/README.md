# Memori + Neon Example

Example showing how to use Memori with Neon serverless Postgres.

[Neon](https://neon.tech) is a serverless Postgres platform that offers instant provisioning, autoscaling, and branching. Since Neon is PostgreSQL-compatible, Memori works seamlessly with it using the standard PostgreSQL driver.

## Getting Started

Sign up for [Neon](https://neon.tech) to get a free serverless Postgres database. Once you create a project, you'll receive a connection string that looks like:

```
postgresql://user:pass@ep-xyz-123.us-east-2.aws.neon.tech/dbname?sslmode=require
```

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   export NEON_CONNECTION_STRING=postgresql://user:pass@ep-xyz-123.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```

3. **Run the example**:
   ```bash
   uv run python main.py
   ```

## How Memori is Used

1. Registers OpenAI client with Memori
2. Configures attribution with `entity_id` (user) and `process_id` (bot/session)
3. Builds Memori schema using `mem.config.storage.build()` to create necessary database tables
4. Runs interactive chat loop where all messages are automatically persisted to Neon
5. Commits after each interaction using `mem.config.storage.adapter.commit()` to save conversation history

## Why Neon?

- **Serverless**: No database management, scales to zero when not in use
- **Fast**: Sub-second cold starts with instant branching
- **PostgreSQL-compatible**: Works with all PostgreSQL tools and libraries
- **Generous free tier**: Perfect for development and small projects
- **Branch your data**: Create database branches like Git branches for testing

## Connection Pooling

This example uses SQLAlchemy's connection pooling with `pool_pre_ping=True` to ensure connections are valid before use. This is especially useful with Neon's serverless architecture where connections may be interrupted.
