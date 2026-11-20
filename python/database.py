"""Қалалық емхана пациенттерінің картотекасына арналған деректер базасы."""
import sqlite3

DB_NAME = "clinic.db"

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS patients (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name   TEXT NOT NULL,
    birth_date  TEXT NOT NULL,
    gender      TEXT NOT NULL CHECK (gender IN ('Ер', 'Әйел')),
    phone       TEXT UNIQUE,
    address     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    specialization  TEXT NOT NULL,
    phone           TEXT UNIQUE,
    cabinet         INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id        INTEGER NOT NULL,
    doctor_id         INTEGER NOT NULL,
    appointment_date  TEXT NOT NULL,
    appointment_time  TEXT NOT NULL,
    reason            TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS medical_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    record_date     TEXT NOT NULL,
    diagnosis       TEXT NOT NULL,
    complaint       TEXT NOT NULL,
    recommendation  TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);
"""


def get_connection(db_name=DB_NAME):
    """Базаға қосылады және сыртқы кілттерді тексеруді қосады."""
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn):
    """Төрт кестені құрады."""
    conn.executescript(CREATE_TABLES_SQL)
    conn.commit()
