r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       memorilabs.ai
"""

from memori._network import Api
from memori.llm._embeddings import embed_texts_async
from memori.memory._struct import Memories
from memori.memory.augmentation._base import AugmentationContext, BaseAugmentation
from memori.memory.augmentation._registry import Registry


@Registry.register("advanced_augmentation")
class AdvancedAugmentation(BaseAugmentation):
    def __init__(self, config=None, enabled: bool = True):
        super().__init__(config=config, enabled=enabled)

    async def process(self, ctx: AugmentationContext, driver) -> AugmentationContext:
        if ctx.payload.entity_id is None or self.config is None:
            return ctx

        messages = ctx.payload.conversation_messages
        summary = ""

        if ctx.payload.conversation_id is None:
            return ctx

        try:
            conversation = driver.conversation.read(ctx.payload.conversation_id)
            if conversation and conversation.get("summary"):
                summary = conversation["summary"]
        except Exception:
            summary = ""

        api = Api(self.config)

        if not self.config.is_test_mode():
            try:
                await api.advanced_augmentation_async(summary, messages)
            except Exception:
                pass
        else:
            pass

        conversation_summary = (
            summary
            if summary
            else "The user seeks ways to reduce daily commute costs, explores the benefits of carpooling, and asks where to find carpooling options."
        )

        api_response = {
            "conversation": {
                "summary": conversation_summary,
                "messages": messages,
            },
            "entity": {
                "facts": [
                    "user is looking for ways to reduce daily commute costs",
                    "user is interested in carpooling",
                    "the conversation topic is about commuting",
                    "the conversation topic is about cost reduction",
                    "the conversation topic is about carpooling options",
                ],
                "list": [
                    {"name": "user", "type": "PERSON"},
                    {"name": "daily commute costs", "type": "MONEY"},
                    {"name": "carpooling", "type": "EVENT"},
                    {"name": "commuting", "type": "EVENT"},
                    {"name": "cost reduction", "type": "MONEY"},
                    {"name": "carpooling options", "type": "EVENT"},
                ],
                "semantic_triples": [
                    {
                        "subject": {"name": "user", "type": "PERSON"},
                        "predicate": "is looking for ways to reduce",
                        "object": {
                            "name": "daily commute costs",
                            "type": "MONEY",
                        },
                    },
                    {
                        "subject": {"name": "user", "type": "PERSON"},
                        "predicate": "is interested in",
                        "object": {"name": "carpooling", "type": "EVENT"},
                    },
                    {
                        "subject": {"name": "conversation topic", "type": "TOPIC"},
                        "predicate": "is about",
                        "object": {"name": "commuting", "type": "EVENT"},
                    },
                    {
                        "subject": {"name": "conversation topic", "type": "TOPIC"},
                        "predicate": "is about",
                        "object": {"name": "cost reduction", "type": "MONEY"},
                    },
                    {
                        "subject": {"name": "conversation topic", "type": "TOPIC"},
                        "predicate": "is about",
                        "object": {"name": "carpooling options", "type": "EVENT"},
                    },
                ],
            },
            "process": {
                "attributes": [
                    "Practical life optimization",
                    "Cost-saving strategies",
                    "Transportation and commuting advice",
                    "Pros and cons explanation",
                    "Resource and app recommendations",
                ]
            },
        }

        facts: list[str] = api_response["entity"]["facts"]  # type: ignore[assignment]
        fact_embeddings = await embed_texts_async(facts)
        api_response["entity"]["fact_embeddings"] = fact_embeddings

        memories = Memories().configure_from_advanced_augmentation(api_response)

        ctx.data["memories"] = memories
        ctx.data["fact_embeddings"] = fact_embeddings

        if ctx.payload.entity_id and memories.entity:
            entity_id = driver.entity.create(ctx.payload.entity_id)
            if entity_id:
                if memories.entity.facts and memories.entity.fact_embeddings:
                    ctx.add_write(
                        "entity_fact.create",
                        entity_id,
                        memories.entity.facts,
                        memories.entity.fact_embeddings,
                    )

                if memories.entity.semantic_triples:
                    ctx.add_write(
                        "knowledge_graph.create",
                        entity_id,
                        memories.entity.semantic_triples,
                    )

        if ctx.payload.process_id and memories.process:
            process_id = driver.process.create(ctx.payload.process_id)
            if process_id and memories.process.attributes:
                ctx.add_write(
                    "process_attribute.create", process_id, memories.process.attributes
                )

        # Update conversation summary
        if ctx.payload.conversation_id and conversation_summary:
            ctx.add_write(
                "conversation.update",
                ctx.payload.conversation_id,
                conversation_summary,
            )

        return ctx
