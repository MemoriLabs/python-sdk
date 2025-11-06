import pytest

from memori.memory.augmentation._base import BaseAugmentation


def test_base_augmentation_init_default():
    aug = BaseAugmentation()
    assert aug.enabled is True


def test_base_augmentation_init_disabled():
    aug = BaseAugmentation(enabled=False)
    assert aug.enabled is False


@pytest.mark.asyncio
async def test_base_augmentation_process_not_implemented():
    aug = BaseAugmentation()
    with pytest.raises(NotImplementedError):
        await aug.process({}, None)
