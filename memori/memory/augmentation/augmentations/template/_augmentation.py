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

import asyncio

import aiohttp

from memori.memory.augmentation._base import AugmentationContext, BaseAugmentation
from memori.memory.augmentation._registry import Registry


@Registry.register("template")
class TemplateAugmentation(BaseAugmentation):
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)

    async def process(self, ctx: AugmentationContext, driver) -> AugmentationContext:
        conversation_id = ctx.payload.get("conversation_id")

        last_message_idx = 0
        if conversation_id:
            try:
                messages = driver.conversation.messages.read(conversation_id)
                last_message_idx = len(messages) if messages else 0
            except Exception:
                conversation_id = None

        await asyncio.sleep(3)

        if aiohttp is None:
            status = "error: aiohttp not installed"
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://api.github.com/zen",
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as response:
                        if response.status == 200:
                            zen_quote = (await response.text()).strip()
                            status = f"success: '{zen_quote}'"
                        else:
                            status = f"HTTP {response.status}"
            except Exception as e:
                status = f"error: {str(e)}"

        ctx.data["zen_quote"] = status

        if conversation_id:
            ctx.add_write(
                "conversation.message.create",
                conversation_id=conversation_id,
                role="assistant",
                type="augmentation",
                content=f"TemplateAugmentation I/O {status} [triggered by message #{last_message_idx}]",
            )
        else:
            ctx.data["template_output"] = f"TemplateAugmentation I/O {status}"

        return ctx
