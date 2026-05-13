import sqlite3
import time
import os
from core import Vote, Block, Chain

def process_event_stream():
    print("Перевіряю таблицю на оновлення...")
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tutorial.db')
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    Vote.fetch_all(cur)
    main_chain = Chain()

    while True:
        cur.execute("SELECT rowid, type, id FROM event_stream WHERE Validate = 0 ORDER BY id")
        events = cur.fetchall()

        if events:
            new_blocks_pool = []

            for row_id, recordType, recordId in events:
                if recordType == "block":
                    cur.execute("SELECT id, view, desc, img FROM BLOCKS WHERE id = ?", (recordId,))
                    row = cur.fetchone()
                    if row:
                        print('block')
                        new_block = Block(id=row[0], view=row[1], desc=row[2], img=row[3])
                        new_blocks_pool.append(new_block)

                elif recordType == "vote":
                    cur.execute("SELECT block_id, voter_id, timestamp, source_id FROM VOTES WHERE block_id = ?",
                                (recordId,))
                    row = cur.fetchone()
                    if row:
                        vote = Vote(block_id=row[0], voter_id=row[1], timestamp=row[2], source_id=row[3])
                        Vote.received_ids.add(vote.block_id)

                cur.execute("UPDATE event_stream SET Validate = 1 WHERE rowid = ?", (row_id,))
            if new_blocks_pool:
                main_chain.process_pool(new_blocks_pool)
                new_blocks_pool.clear()

            con.commit()

            print("\nПоточний ланцюжок:")
            if not main_chain.blocks:
                print("Ланцюжок порожній.")
            for c in main_chain.blocks:
                print(c)
            print("-------------------------")

        else:
            print("Немає нових даних, чекаю...")

        time.sleep(7)

if __name__ == "__main__":
    process_event_stream()