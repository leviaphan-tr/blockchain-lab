import pytest
from pydantic import ValidationError
from processor.core import Block, Vote, Chain

def test_block_validation_success():
    block = Block(id="0x1A2B3C", view=0, desc="Genesis block")
    assert block.id == "0x1A2B3C"
    assert block.view == 0


def test_block_validation_failures():

    with pytest.raises(ValidationError):
        Block(id="0x123", view=-1, desc="Bad view")

    with pytest.raises(ValidationError):
        Block(id="not_hex_id", view=1, desc="Bad ID")

def test_chain_try_add_logic():
    chain = Chain()

    Vote.received_ids = {"0x0", "0x1", "0x2"}

    block_0 = Block(id="0x0", view=0, desc="Блок 0")
    block_1 = Block(id="0x1", view=1, desc="Блок 1")
    block_jump = Block(id="0x2", view=3, desc="Пропуск view")
    block_no_vote = Block(id="0x99", view=2, desc="Немає голосу")

    #має пройти, бо view=0 і є голос
    assert chain.try_add(block_0) is True
    assert len(chain.blocks) == 1

    #має теж пройти бо наступний
    assert chain.try_add(block_1) is True
    assert chain.hash == "0x1"

    #має відхилити
    assert chain.try_add(block_1) is False

    #має відхилити через скачок view
    assert chain.try_add(block_jump) is False

    assert chain.try_add(block_no_vote) is False
    assert len(chain.blocks) == 2