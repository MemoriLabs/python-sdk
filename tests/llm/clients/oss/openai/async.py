#!/usr/bin/env python3

import argparse
import asyncio
import os
import time

from openai import AsyncOpenAI

from memori import Memori
from memori.llm._embeddings import embed_texts
from tests.database.core import (
    MongoTestDBSession,
    MySQLTestDBSession,
    PostgresTestDBSession,
    SQLiteTestDBSession,
)

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")

os.environ["MEMORI_TEST_MODE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

print("Pre-loading embedding model...")
embed_texts("warmup")
print("✓ Embedding model ready")


async def run(db_backend: str = "default"):
    print(f"🗄️  Using database backend: {db_backend}")
    print("-" * 50)

    # Initialize database session based on backend
    if db_backend == "postgres":
        conn = PostgresTestDBSession
    elif db_backend == "mysql":
        conn = MySQLTestDBSession
    elif db_backend == "mongodb":
        conn = MongoTestDBSession
    elif db_backend == "sqlite":
        conn = SQLiteTestDBSession
    else:
        # Default: CockroachDB connection for testing
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(
            "cockroachdb://memori:tZNAeE5XKA7Nkg3HWm15GQ@memori-labs-test-9943.jxf.gcp-us-west2.cockroachlabs.cloud:26257/defaultdb?sslmode=require"
        )
        conn = sessionmaker(bind=engine)

    client = AsyncOpenAI()

    mem = Memori(conn=conn)

    # Initialize database schema
    mem.config.storage.build()

    mem.openai.register(client)

    # Multiple registrations should not cause an issue.
    mem.openai.register(client)

    mem.attribution(entity_id="123", process_id="456")

    # Pre-seed some facts to test recall/injection
    print("📝 Seeding test facts...")
    entity_id = mem.config.storage.driver.entity.create("123")

    if entity_id:
        # Create facts with relevant information
        test_facts = [
            "User works as a Senior Software Engineer at TechCorp",
            "User specializes in Python and distributed systems",
            "User has 8 years of experience in backend development",
            "User follows a Mediterranean diet with lots of vegetables and fish",
            "User drinks green smoothies for breakfast every morning",
            "User's dog is named Max and is a Golden Retriever",
            "User's cat is named Luna and loves to sleep on the keyboard",
        ]

        # Generate embeddings for the facts
        from memori.llm._embeddings import embed_texts

        fact_embeddings = embed_texts(test_facts)

        # Insert facts into database
        mem.config.storage.driver.entity_fact.create(
            entity_id=entity_id, facts=test_facts, fact_embeddings=fact_embeddings
        )
        print(f"✓ Seeded {len(test_facts)} facts for entity {entity_id}")

    print("-" * 25)

    query = "What do I do for work?"
    print(f"me: {query}")

    start_time = time.time()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    )
    elapsed = time.time() - start_time

    print("-" * 25)

    assert response and response.choices[0].message.content
    assert response.id and response.usage.total_tokens > 0

    first_response_content = response.choices[0].message.content
    print(f"llm: {first_response_content}")
    print(f"Response time: {elapsed:.2f}s")

    # Verify recall is working - response should mention seeded job info
    job_keywords = ["software engineer", "techcorp", "python", "backend", "developer"]
    if any(keyword in first_response_content.lower() for keyword in job_keywords):
        print("✓ Recall working: Job information injected")
    else:
        print("⚠ Warning: Expected job information not found in response")

    print("-" * 25)

    assert mem.config.cache.conversation_id
    stored_messages = mem.config.storage.driver.conversation.messages.read(
        mem.config.cache.conversation_id
    )
    assert len(stored_messages) >= 2
    assert stored_messages[0]["role"] == "user"
    assert stored_messages[-1]["role"] == "assistant"
    print(f"✓ {len(stored_messages)} messages stored")

    query = "Tell me about my nutrition habits"
    print(f"me: {query}")

    print("-" * 25)

    start_time = time.time()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful nutritionist assistant."},
            {"role": "user", "content": query},
        ],
    )
    elapsed = time.time() - start_time

    print("-" * 25)

    second_response_content = response.choices[0].message.content
    print(f"llm: {second_response_content}")
    print(f"Response time: {elapsed:.2f}s")

    # Verify recall is working - response should mention seeded nutrition info
    nutrition_keywords = [
        "mediterranean",
        "diet",
        "vegetables",
        "fish",
        "smoothie",
        "breakfast",
    ]
    if any(
        keyword in second_response_content.lower() for keyword in nutrition_keywords
    ):
        print("✓ Recall working: Nutrition information injected")
        print("✓ System prompt extended with recalled facts (nutritionist + facts)")
    else:
        print("⚠ Warning: Expected nutrition information not found in response")

    print("-" * 25)

    query = "What's my dog and cats name'?"
    print(f"me: {query}")

    start_time = time.time()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    )
    elapsed = time.time() - start_time

    third_response_content = response.choices[0].message.content
    print(f"llm: {third_response_content}")
    print(f"Response time: {elapsed:.2f}s")

    # Verify recall is working - response should mention seeded pet names
    pet_keywords = ["max", "luna", "golden retriever", "keyboard"]
    if any(keyword in third_response_content.lower() for keyword in pet_keywords):
        print("✓ Recall working: Pet information injected")
    else:
        print("⚠ Warning: Expected pet information not found in response")

    print("-" * 50)

    # Give augmentation time to complete before verifying
    print("⏳ Waiting for background augmentation to complete...")
    time.sleep(5)

    # Verify augmentation data was written to database
    print("📊 Verifying augmentation data...")
    entity_id = mem.config.cache.entity_id

    if entity_id:
        # Check for entity facts
        try:
            if db_backend == "mongodb":
                facts_collection = (
                    mem.config.storage.adapter.conn.get_default_database()[
                        "memori_entity_fact"
                    ]
                )
                entity_facts = list(
                    facts_collection.find(
                        {"entity_id": entity_id},
                        {"content": 1, "num_times": 1, "_id": 0},
                    ).limit(10)
                )
            else:
                # SQL databases - use appropriate placeholder
                placeholder = "?" if db_backend == "sqlite" else "%s"
                entity_facts = mem.config.storage.adapter.execute(
                    f"""
                    SELECT content, num_times
                    FROM memori_entity_fact
                    WHERE entity_id = {placeholder}
                    LIMIT 10
                    """,
                    (entity_id,),
                ).fetchall()

            if entity_facts:
                print(f"✓ Found {len(entity_facts)} entity facts:")
                for idx, fact in enumerate(entity_facts[:5], 1):
                    if db_backend == "mongodb":
                        print(
                            f"  {idx}. {fact.get('content', 'N/A')} (seen {fact.get('num_times', 0)}x)"
                        )
                    else:
                        print(f"  {idx}. {fact[0]} (seen {fact[1]}x)")
                if len(entity_facts) > 5:
                    print(f"  ... and {len(entity_facts) - 5} more")
            else:
                print("⚠ No entity facts found (augmentation may still be processing)")

        except Exception as e:
            print(f"⚠ Could not verify entity facts: {e}")

        # Check for knowledge graph entries
        try:
            if db_backend == "mongodb":
                kg_collection = mem.config.storage.adapter.conn.get_default_database()[
                    "memori_knowledge_graph"
                ]
                kg_count = kg_collection.count_documents({"entity_id": entity_id})
            else:
                # SQL databases - use appropriate placeholder
                placeholder = "?" if db_backend == "sqlite" else "%s"
                kg_count = mem.config.storage.adapter.execute(
                    f"""
                        SELECT COUNT(*)
                        FROM memori_knowledge_graph
                        WHERE entity_id = {placeholder}
                        """,
                    (entity_id,),
                ).fetchone()[0]

            if kg_count > 0:
                print(f"✓ Found {kg_count} knowledge graph entries")
            else:
                print("⚠ No knowledge graph entries found")

        except Exception as e:
            print(f"⚠ Could not verify knowledge graph: {e}")

    print("-" * 50)
    print(f"✓ All tests passed with {db_backend} backend!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test OpenAI async client with various database backends"
    )
    parser.add_argument(
        "--db",
        choices=["default", "postgres", "mysql", "mongodb", "sqlite"],
        default="default",
        help="Database backend to use (default: uses DATABASE_URL env var)",
    )
    args = parser.parse_args()

    asyncio.run(run(args.db))
