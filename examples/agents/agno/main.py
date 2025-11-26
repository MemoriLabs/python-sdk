"""
Agno + Memori Simple Example

Demonstrates how to integrate Memori with Agno agents for persistent memory.

This example creates a simple assistant that:
1. Remembers all conversations
2. Can reference past interactions
3. Provides personalized responses based on history

Key Features:
- Automatic conversation tracking
- Persistent memory across sessions
- Simple single-agent setup
- No external APIs needed (except OpenAI)

Requirements:
- Environment variables:
  - OPENAI_API_KEY
"""

from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from memori import Memori

# Load environment variables
load_dotenv()

# Database setup
cwd = Path(__file__).parent.resolve()
db_path = cwd.joinpath("agno_memori.db")
database_url = f"sqlite:///{db_path}"

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1")).scalar_one()
    print(f"Database connection OK: {result}")


class PersonalAssistantWithMemory:
    """A simple personal assistant with Memori v3 memory capabilities"""

    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = OpenAI()

        # Initialize Memori and register the OpenAI client
        # This enables automatic conversation tracking
        self.mem = Memori(conn=SessionLocal).openai.register(self.openai_client)

        # Set attribution - user is the entity, assistant is the process
        self.mem.attribution(entity_id="user_001", process_id="personal_assistant")

        # Build database schema
        self.mem.config.storage.build()

        self.agent = None

    def create_memory_tool(self):
        """Create a memory recall tool for the Agno agent"""

        def recall_memory(query: str) -> str:
            """Search the user's memory for relevant information.

            Args:
                query: The search query to find relevant memories about the user

            Returns:
                A summary of relevant memories found, or a message if no memories found
            """
            facts = self.mem.recall(query, limit=5)

            if not facts:
                return "No relevant memories found."

            # Format the facts into a readable response
            memory_lines = []
            for i, fact in enumerate(facts, 1):
                similarity = fact.get("similarity", 0)
                content = fact.get("content", "")
                memory_lines.append(f"{i}. {content} (relevance: {similarity:.2f})")

            return "Relevant memories:\n" + "\n".join(memory_lines)

        return recall_memory

    def create_agent(self):
        """Create a personal assistant agent with memory"""
        # Create the memory tool
        memory_tool = self.create_memory_tool()

        agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini", api_key=self.openai_client.api_key),
            tools=[memory_tool],
            description=dedent(
                """\
                You are a helpful personal assistant with MEMORY CAPABILITIES!

                Your abilities:
                - Remember all past conversations with the user
                - Reference previous discussions naturally using the recall_memory tool
                - Learn user preferences over time
                - Provide personalized, context-aware responses

                Your personality:
                - Friendly and approachable
                - Helpful and proactive
                - Good at remembering details about the user
                - Natural in referencing past conversations
            """
            ),
            instructions=dedent(
                """\
                When interacting with users:
                1. ALWAYS use the recall_memory tool to check for relevant past information
                2. Reference previous discussions when appropriate
                3. Remember user preferences and details they've shared
                4. Provide personalized responses based on what you know
                5. Be natural and conversational

                IMPORTANT: Use recall_memory at the start of each conversation to recall relevant context!
            """
            ),
            markdown=True,
        )
        return agent

    def chat(self, message: str):
        """Send a message to the assistant"""
        if self.agent is None:
            self.agent = self.create_agent()

        print(f"\nYou: {message}")
        print("-" * 80)

        # Run the agent - Agno will use its internal OpenAI client
        # which won't trigger Memori's interception
        result = self.agent.run(message)

        # Manually record the conversation using the registered OpenAI client
        # This ensures Memori captures it
        self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": str(result.content)},
            ],
        )

        # Commit to persist conversation
        self.mem.config.storage.adapter.commit()

        return result


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AGNO + MEMORI v3 PERSONAL ASSISTANT")
    print("=" * 80)
    print("\nThis example demonstrates a simple Agno agent with Memori v3 memory.")
    print("All conversations are automatically tracked and remembered.\n")
    print("=" * 80)

    assistant = PersonalAssistantWithMemory()

    # Example conversation demonstrating memory
    print("\n Starting conversation...\n")

    # First interaction - user shares information
    assistant.chat("Hi! My name is Alice and I love Italian food, especially pizza.")

    # Second interaction - user asks a question
    assistant.chat("What's a good recipe for homemade pizza dough?")

    # Third interaction - testing memory
    assistant.chat("What's my name and what food do I like?")

    # Fourth interaction - showing personalized response
    assistant.chat("Can you recommend a restaurant for dinner tonight?")

    print("\n" + "=" * 80)
    print(f"✓ All conversations saved to database: {db_path}")
    print(
        "\nMemori automatically tracked all conversations and will inject relevant context in future sessions!"
    )
    print(
        "\nTry running this script again - the assistant will remember your previous conversations!"
    )
    print("=" * 80)
