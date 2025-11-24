# Memori Neon Example

Example showing how to use Memori with [Neon serverless Postgres](https://neon.com/).

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
3. Builds Memori schema using `build()` to create necessary database tables
4. Runs interactive chat loop where all messages are automatically persisted to Neon
5. Commits after each interaction to save conversation history
