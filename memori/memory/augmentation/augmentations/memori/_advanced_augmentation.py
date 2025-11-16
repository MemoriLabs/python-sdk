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

from memori.memory.augmentation._base import AugmentationContext, BaseAugmentation
from memori.memory.augmentation._registry import Registry


@Registry.register("advanced_augmentation")
class AdvancedAugmentation(BaseAugmentation):
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)

    async def process(self, ctx: AugmentationContext, driver) -> AugmentationContext:
        return ctx
