import subprocess
import sys
import os
import sqlite3
import time

BLUE, GREEN, YELLOW, RED, RESET, BOLD = "\033[94m", "\033[92m", "\033[93m", "\033[91m", "\033[0m", "\033[1m"


def get_db_status():
    db_path = os.path.join(os.path.dirname(__file__), 'tutorial.db')
    if not os.path.exists(db_path): return f"{RED}Відсутня{RESET}"

    try:
        # Режим розпаралелювання, щоб база не "тупила"
        con = sqlite3.connect(db_path, timeout=0.5)
        con.execute("PRAGMA journal_mode=WAL;")
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM BLOCKS")
        blocks = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM event_stream WHERE Validate = 0")
        pending = cur.fetchone()[0]
        con.close()
        return f"{GREEN}OK{RESET} (Блоків: {blocks}, Очікують: {pending})"
    except:
        return f"{YELLOW}База зайнята{RESET}"


def run_script(path):
    fpath = os.path.join(os.path.dirname(__file__), path)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(__file__)
    try:
        subprocess.run([sys.executable, fpath], env=env)
    except KeyboardInterrupt:
        pass


def main():
    while True:
        # Чистимо екран тільки якщо це справжній термінал
        if sys.stdout.isatty(): os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{BLUE}{'=' * 45}{RESET}\n{BOLD}   BLOCKCHAIN MANAGER v2.3{RESET}\n{BLUE}{'=' * 45}{RESET}")
        print(f" Статус: {get_db_status()}")
        print(f"{BLUE}{'-' * 45}{RESET}")
        print(f" 1. [Generator]  2. [Updater]  3. [Processor]")
        print(f" 4. {RED}[Reset]{RESET}      0. {BOLD}[EXIT]{RESET}")
        print(f"{BLUE}{'=' * 45}{RESET}")

        try:
            choice = input(f"\n{BLUE}Дія > {RESET}").strip()
        except KeyboardInterrupt:
            sys.exit(0)

        if choice == "1":
            run_script("data/generate_test_data.py")
        elif choice == "2":
            run_script("updater/updater.py")
        elif choice == "3":
            run_script("processor/BlockProcessor.py")
        elif choice == "4":
            if input("Видалити базу? (y/n): ").lower() == 'y':
                if os.path.exists("tutorial.db"): os.remove("tutorial.db")
        elif choice == "0":
            sys.exit(0)
        else:
            time.sleep(0.2)


if __name__ == "__main__":
    main()