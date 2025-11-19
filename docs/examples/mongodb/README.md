# Memori MongoDB Example

Example showing how to use Memori with MongoDB.

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   export MONGODB_CONNECTION_STRING=mongodb+srv://user:password@cluster.mongodb.net/dbname
   ```

3. **Run the example**:
   ```bash
   uv run python main.py
   ```

## How Memori is Used

1. Registers OpenAI client with Memori
2. Configures attribution with `entity_id` (user) and `process_id` (bot/session)
3. Builds Memori collections using `build()` to create necessary database collections
4. Runs interactive chat loop where all messages are automatically persisted to MongoDB
5. No explicit commits needed - MongoDB writes are immediate
