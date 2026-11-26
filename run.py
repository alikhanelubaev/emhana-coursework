"""SQLite файлдарын орындайтын жұқа іске қосқыш; бизнес логика sql/ ішінде."""
from pathlib import Path
import json
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent


def execute(conn, path, params):
    print(f"\n--- {path.relative_to(ROOT)} ---")
    buffer = ""
    errors = 0
    for line in path.read_text(encoding="utf-8").splitlines(True):
        buffer += line
        if not sqlite3.complete_statement(buffer):
            continue
        expected = next((s.split(":", 1)[1].strip() for s in buffer.splitlines()
                         if s.strip().startswith("-- expect-error:")), None)
        try:
            cursor = conn.execute(buffer, params)
        except sqlite3.IntegrityError as error:
            if expected is None or expected not in str(error):
                raise
            errors += 1
            print("PASS expected rejection:", expected)
        else:
            if expected is not None:
                raise AssertionError(f"Expected rejection: {expected}")
            if cursor.description:
                print(" | ".join(c[0] for c in cursor.description))
                for row in cursor:
                    print(" | ".join(str(v) for v in row))
        buffer = ""
    if buffer.strip() and any(s.strip() and not s.lstrip().startswith("--") for s in buffer.splitlines()):
        raise ValueError(f"Unterminated SQL: {path}")
    return errors


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "clinic.db")
    if name != ":memory:":
        Path(name).resolve().parent.mkdir(parents=True, exist_ok=True)
    params = json.loads((ROOT / "sql" / "parameters.json").read_text(encoding="utf-8"))
    conn = sqlite3.connect(name, isolation_level=None)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        scripts = sorted((ROOT / "sql").glob("0*.sql"))
        scripts += sorted((ROOT / "sql" / "queries").glob("*.sql"))
        scripts += [ROOT / "sql" / "patient_card.sql"]
        scripts += sorted((ROOT / "sql" / "examples").glob("*.sql"))
        if name == ":memory:":
            scripts += sorted((ROOT / "sql" / "tests").glob("*.sql"))
        errors = sum(execute(conn, path, params) for path in scripts)
        print(f"\nOK: {len(scripts)} SQL files; {errors} expected rejections; database: {name}")
    finally:
        conn.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
