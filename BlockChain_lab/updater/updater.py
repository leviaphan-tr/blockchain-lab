import sqlite3
import csv
import os
from pydantic import ValidationError
from processor.core import Block, Vote, Source, Person


def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tutorial.db')
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS event_stream (
            type TEXT,
            id TEXT,
            Validate INTEGER DEFAULT 0
        )
    ''')
    con.commit()
    return con


def insert_block(cur, block_id, view, desc="", img=None):
    try:
        data = Block(id=block_id, view=view, desc=desc, img=img)
    except ValidationError as e:
        print(f"Error Block (ID: {block_id}):\n{e}")
        return False

    cur.execute("INSERT INTO BLOCKS (id, view, desc, img) VALUES (?, ?, ?, ?)",
                (data.id, data.view, data.desc, data.img))
    cur.execute("INSERT INTO event_stream (type, id) VALUES (?, ?)", ("block", data.id))
    return True


def insert_vote(cur, block_id, voter_id, timestamp, source_id):
    try:
        data = Vote(block_id=block_id, voter_id=voter_id, timestamp=timestamp, source_id=source_id)
    except ValidationError as e:
        print(f"Error Vote (Block ID: {block_id}):\n{e}")
        return False

    cur.execute("INSERT INTO VOTES (block_id, voter_id, timestamp, source_id) VALUES (?, ?, ?, ?)",
                (data.block_id, data.voter_id, data.timestamp, data.source_id))
    cur.execute("INSERT INTO event_stream (type, id) VALUES (?, ?)", ("vote", data.block_id))
    return True


def insert_person(cur, person_id, name, addr):
    try:
        data = Person(id=person_id, name=name, addr=addr)
    except ValidationError as e:
        print(f"Error Person (ID: {person_id}):\n{e}")
        return False

    cur.execute("INSERT INTO PERSONS (id, name, addr) VALUES (?, ?, ?)",
                (data.id, data.name, data.addr))
    cur.execute("INSERT INTO event_stream (type, id) VALUES (?, ?)", ("person", data.id))
    return True


def insert_source(cur, source_id, ip_addr, country_code):
    try:
        data = Source(id=source_id, ip_addr=ip_addr, country_code=country_code)
    except ValidationError as e:
        print(f"Error Source (ID: {source_id}):\n{e}")
        return False

    cur.execute("INSERT INTO SOURCES (id, ip_addr, country_code) VALUES (?, ?, ?)",
                (data.id, data.ip_addr, data.country_code))
    cur.execute("INSERT INTO event_stream (type, id) VALUES (?, ?)", ("source", data.id))
    return True


DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')


def bulk_from_csv(filename):
    file_path = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {os.path.abspath(file_path)}")
        return

    con = connect_db()
    cur = con.cursor()
    success, error = 0, 0

    try:
        with open(file_path, encoding="utf-8") as data:
            reader = csv.reader(data)
            next(reader)
            for row in reader:
                rtype = row[0].strip()
                ok = False
                if rtype == "block":
                    ok = insert_block(cur, row[1], row[2], row[3], None)
                elif rtype == "vote":
                    ok = insert_vote(cur, row[4], row[5], row[6], row[7])
                elif rtype == "person":
                    ok = insert_person(cur, row[1], row[8], row[9])
                elif rtype == "source":
                    ok = insert_source(cur, row[1], row[10], row[11])

                if ok:
                    success += 1
                else:
                    error += 1
        con.commit()
        print(f"\nImport {filename}: {success} success, {error} error.")
    finally:
        con.close()


def input_mode():
    con = connect_db()
    cur = con.cursor()
    while True:
        rtype = input("\nType (block/vote/person/source/exit): ").strip().lower()
        if rtype == "exit": break
        if rtype == "block":
            if insert_block(cur, input("id: "), input("view: "), input("desc: ")):
                con.commit()
        elif rtype == "vote":
            if insert_vote(cur, input("bid: "), input("vid: "), input("time: "), input("sid: ")):
                con.commit()
        elif rtype == "person":
            if insert_person(cur, input("id: "), input("name: "), input("addr: ")):
                con.commit()
        elif rtype == "source":
            if insert_source(cur, input("id: "), input("ip: "), input("code: ")):
                con.commit()
    con.close()


if __name__ == "__main__":
    mode = input("Mode (csv/input): ").strip().lower()
    if mode == "csv":
        bulk_from_csv(input("File: "))
    elif mode == "input":
        input_mode()