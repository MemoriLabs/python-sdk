# Memori + Agno Example

This example demonstrates how to use Memori v3 with Agno agents to create AI assistants with persistent memory.

## Overview

This example shows how Memori can be integrated with Agno agents to provide:
- **Persistent memory** across agent sessions
- **Automatic conversation tracking** for all agent interactions
- **Context-aware responses** based on past conversations
- **Simple, single-agent setup** with minimal dependencies

## Use Case

Build a personal assistant that:
1. Remembers all conversations with users
2. References past discussions naturally
3. Learns user preferences over time
4. Provides personalized, context-aware responses

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the example**:
   ```bash
   uv run python main.py
   ```

## How It Works

1. **Memori registers the OpenAI client** used by Agno agents
2. **Attribution tracks** the user and assistant conversations
3. **Conversations are automatically stored** with vector embeddings
4. **Relevant context is injected** into agent prompts based on semantic search
5. **Agent references** past conversations naturally in responses

## Example Interactions

```
You: "Hi! My name is Alice and I love Italian food, especially pizza."
Assistant: "Nice to meet you, Alice! It's great to know you love Italian food..."

You: "What's a good recipe for homemade pizza dough?"
Assistant: "Since you love pizza, here's a great recipe..."

You: "What's my name and what food do I like?"
Assistant: "Your name is Alice, and you mentioned you love Italian food, especially pizza!"

You: "Can you recommend a restaurant for dinner tonight?"
Assistant: "Given your love for Italian food and pizza, I'd recommend..."
```

## Running the Example

When you run the example, it will:
1. Create a personal assistant with memory
2. Have a sample conversation demonstrating memory capabilities
3. Save all conversations to `agno_memori.sqlite`
4. Show how the assistant remembers user information

Run it multiple times to see how the assistant builds on previous conversations!
