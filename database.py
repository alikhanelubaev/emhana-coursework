"""SQLite қосылымы, схема және бір рет орындалатын бастапқы толтыру."""
from contextlib import contextmanager
from pathlib import Path
import os
import sqlite3
import unicodedata
from security import hash_password
from seed import insert_seed

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "clinic.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 full_name TEXT NOT NULL CHECK(length(trim(full_name)) BETWEEN 2 AND 150),
 birth_date TEXT NOT NULL CHECK(length(birth_date)=10 AND date(birth_date,'+0 days') IS NOT NULL AND date(birth_date,'+0 days')=birth_date),
 gender TEXT NOT NULL CHECK(gender IN ('Ер','Әйел')),
 phone TEXT UNIQUE NOT NULL,
 address TEXT NOT NULL CHECK(length(trim(address)) BETWEEN 2 AND 2000)
);
CREATE TABLE IF NOT EXISTS doctors (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 full_name TEXT NOT NULL CHECK(length(trim(full_name)) BETWEEN 2 AND 150),
 specialization TEXT NOT NULL CHECK(length(trim(specialization)) BETWEEN 2 AND 150),
 phone TEXT UNIQUE NOT NULL,
 cabinet INTEGER NOT NULL CHECK(cabinet BETWEEN 1 AND 9999)
);
CREATE TABLE IF NOT EXISTS appointments (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 patient_id INTEGER NOT NULL REFERENCES patients(id) ON UPDATE CASCADE ON DELETE RESTRICT,
 doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON UPDATE CASCADE ON DELETE RESTRICT,
 appointment_date TEXT NOT NULL CHECK(length(appointment_date)=10 AND date(appointment_date,'+0 days') IS NOT NULL AND date(appointment_date,'+0 days')=appointment_date),
 appointment_time TEXT NOT NULL CHECK(length(appointment_time)=5 AND time(appointment_time) IS NOT NULL),
 reason TEXT NOT NULL CHECK(length(trim(reason)) BETWEEN 2 AND 2000),
 UNIQUE(doctor_id,appointment_date,appointment_time),
 UNIQUE(patient_id,appointment_date,appointment_time)
);
CREATE TABLE IF NOT EXISTS medical_records (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 patient_id INTEGER NOT NULL REFERENCES patients(id) ON UPDATE CASCADE ON DELETE RESTRICT,
 record_date TEXT NOT NULL CHECK(length(record_date)=10 AND date(record_date,'+0 days') IS NOT NULL AND date(record_date,'+0 days')=record_date),
 diagnosis TEXT NOT NULL CHECK(length(trim(diagnosis)) BETWEEN 2 AND 150),
 complaint TEXT NOT NULL CHECK(length(trim(complaint)) BETWEEN 2 AND 2000),
 recommendation TEXT NOT NULL CHECK(length(trim(recommendation)) BETWEEN 2 AND 2000)
);
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT NOT NULL UNIQUE COLLATE NOCASE,
 display_name TEXT NOT NULL,
 password_hash TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN ('admin','registrar','doctor')),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
 failed_attempts INTEGER NOT NULL DEFAULT 0,
 locked_until TEXT,
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE TABLE IF NOT EXISTS audit_log (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
 action TEXT NOT NULL,
 entity TEXT NOT NULL,
 record_id INTEGER,
 details TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date,appointment_time);
CREATE INDEX IF NOT EXISTS idx_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_records_diagnosis ON medical_records(diagnosis);
"""


def database_path(db_path=None) -> Path:
    return Path(db_path or os.environ.get("EMHANA_DB_PATH") or DEFAULT_DB_PATH).resolve()


def fold(value) -> str:
    return unicodedata.normalize("NFKC", str(value or "")).casefold()


def get_connection(db_path=None) -> sqlite3.Connection:
    path = database_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=10000")
    conn.create_function("casefold", 1, fold, deterministic=True)
    return conn


@contextmanager
def connection(db_path=None):
    conn = get_connection(db_path)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def initialize_database(db_path=None, seed=True):
    with connection(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        conn.execute("BEGIN IMMEDIATE")
        if not conn.execute("SELECT 1 FROM app_meta WHERE key='initialized'").fetchone():
            if seed and not conn.execute("SELECT 1 FROM patients LIMIT 1").fetchone():
                insert_seed(conn)
            conn.execute(
                "INSERT INTO users(username,display_name,password_hash,role) VALUES (?,?,?,?)",
                ("admin", "Жүйе әкімшісі", hash_password("Clinic2026"), "admin"),
            )
            conn.execute("INSERT INTO app_meta VALUES ('initialized','1')")
        conn.execute("PRAGMA user_version=1")


if __name__ == "__main__":
    initialize_database()
    print(f"Деректер базасы дайын: {database_path()}")
