from datetime import datetime
from pydantic import BaseModel, Field
from typing import ClassVar
import sqlite3

class Block(BaseModel):
    id: str = Field(pattern=r'^(0x)?[0-9a-fA-F]+$')
    view: int = Field(ge=0)
    desc: str
    img: bytes | None = None

    @classmethod
    def fetch_all(cls, cur: sqlite3.Cursor):
        cur.execute("SELECT id, view, desc, img FROM BLOCKS")
        return [cls(id=row[0], view=row[1], desc=row[2], img=row[3])
                for row in cur.fetchall()]

class Source(BaseModel):
    id: int = Field(ge=0)
    ip_addr: str = Field(pattern=r'^(\d{1,3}\.){3}\d{1,3}$')
    country_code: str = Field(pattern=r'^([A-Z]{2})$')

    @classmethod
    def fetch_all(cls, cur: sqlite3.Cursor):
        cur.execute("SELECT id, ip_addr, country_code FROM SOURCES")
        return [cls(id=row[0], ip_addr=row[1], country_code=row[2])
                for row in cur.fetchall()]

class Vote(BaseModel):
    block_id: str = Field(pattern=r'^(0x)?[0-9a-fA-F]+$')
    voter_id: int = Field(ge=0)
    timestamp: datetime
    source_id: int = Field(ge=0)
    received_ids: ClassVar[set[str]] = set()

    @classmethod
    def fetch_all(cls, cur: sqlite3.Cursor):
        cur.execute("SELECT block_id, voter_id, timestamp, source_id FROM VOTES")
        rows = cur.fetchall()
        votes = []
        for row in rows:
            vote = cls(block_id=row[0], voter_id=row[1], timestamp=row[2], source_id=row[3])
            cls.received_ids.add(vote.block_id)
            votes.append(vote)
        return votes

class Person(BaseModel):
    id: int = Field(ge=0)
    name: str = Field(pattern=r"^[A-ZА-ЯІЇЄҐ][a-zа-яіїєґ']+ [A-ZА-ЯІЇЄҐ][a-zа-яіїєґ']+$",)
    addr: str

    @classmethod
    def fetch_all(cls, cur: sqlite3.Cursor):
        cur.execute("SELECT id, name, addr FROM PERSONS")
        return [cls(id=row[0], name=row[1], addr=row[2])
                for row in cur.fetchall()]

class Chain(BaseModel):
    blocks: list[Block] = Field(default_factory=list)

    def process_pool(self, all_blocks: list[Block]):
        sorted_blocks = sorted(all_blocks, key=lambda x: x.view)
        for block in sorted_blocks :
            self.try_add(block)

    def try_add(self, new_block: Block) -> bool:
        has_vote = new_block.id in Vote.received_ids
        if not self.blocks:
            view_ok = (new_block.view == 0)
        else:
            last_block = self.blocks[-1]
            view_ok = (new_block.view - last_block.view in [0, 1])

        if has_vote and view_ok:
            self.blocks.append(new_block)
            return True
        return False