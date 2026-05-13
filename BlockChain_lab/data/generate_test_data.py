import csv
import os
import hashlib
from datetime import datetime


def generate_unified_csv():
    # Визначаємо шлях до папки, де лежить скрипт (data/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "data.csv")

    # Структура заголовків згідно з індексами в updater.py:
    # 0:type, 1:id, 2:view, 3:desc, 4:block_id, 5:voter_id, 6:timestamp,
    # 7:source_id, 8:name, 9:addr, 10:ip, 11:country
    headers = [
        "type", "id", "view", "desc", "block_id", "voter_id",
        "timestamp", "source_id", "name", "addr", "ip", "country"
    ]

    rows = []

    # 1. Геруємо Sources (згідно з Regex у core.py)
    sources = [
        ["source", "1", "", "", "", "", "", "", "", "", "192.168.1.10", "UA"],
        ["source", "2", "", "", "", "", "", "", "", "", "104.28.10.55", "US"]
    ]
    rows.extend(sources)

    # 2. Генеруємо Persons (згідно з Regex: Ім'я Прізвище)
    persons = [
        ["person", "1001", "", "", "", "", "", "", "Олександр Якушенков", "Гуртожиток №2", "", ""],
        ["person", "1002", "", "", "", "", "", "", "Артем Степаненко", "Гуртожиток №3", "", ""]
    ]
    rows.extend(persons)

    # 3. Генеруємо Блоки та Голоси
    for i in range(10):
        block_id = "0x" + hashlib.md5(f"block_{i}".encode()).hexdigest()

        # Запис для Block
        rows.append([
            "block", block_id, i, f"Тестовий блок стовпця {i}",
            "", "", "", "", "", "", "", ""
        ])

        # Запис для Vote (пов'язаний з цим блоком)
        rows.append([
            "vote", "", "", "",
            block_id, 1001 + (i % 2), datetime.now().isoformat(), 1 + (i % 2),
            "", "", "", ""
        ])

    # Запис у файл
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Успіх! Файл згенеровано за шляхом: {file_path}")


if __name__ == "__main__":
    generate_unified_csv()