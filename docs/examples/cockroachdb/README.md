# Memori CockroachDB Example

*Memori + CockroachDB* brings durable, distributed memory to AI — instantly, globally, and at any scale. Memori transforms conversations into structured, queryable intelligence, while CockroachDB keeps that memory available, resilient, and consistently accurate across regions. Deploy and scale effortlessly from prototype to production with zero downtime on enterprise-grade infrastructure. Give your AI a foundation to remember, reason, and evolve — with the simplicity of cloud and the reliability and power of distributed SQL.

Sign up for [Cockroach Cloud](https://www.cockroachlabs.com/product/cloud/).

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

## How Memori is Used

1. Registers OpenAI client with Memori
2. Configures attribution with `parent_id` (user) and `process_id` (bot/session)
3. Builds Memori schema using `build()` to create necessary database tables
4. Runs interactive chat loop where all messages are automatically persisted to CockroachDB
5. Commits after each interaction to save conversation history
