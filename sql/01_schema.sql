-- Курстықтың 2.2–2.4 және 3.2 бөлімдері: кілттер, байланыстар, шектеулер.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 full_name TEXT NOT NULL CHECK(length(trim(full_name)) BETWEEN 2 AND 150),
 birth_date TEXT NOT NULL CHECK(length(birth_date)=10 AND date(birth_date,'+0 days') IS NOT NULL AND date(birth_date,'+0 days')=birth_date),
 gender TEXT NOT NULL CHECK(gender IN ('Ер','Әйел')),
 phone TEXT UNIQUE NOT NULL CHECK(length(phone) BETWEEN 11 AND 16 AND substr(phone,1,1)='+' AND substr(phone,2) NOT GLOB '*[^0-9]*'),
 address TEXT NOT NULL CHECK(length(trim(address)) BETWEEN 2 AND 2000)
);
CREATE TABLE IF NOT EXISTS doctors (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 full_name TEXT NOT NULL CHECK(length(trim(full_name)) BETWEEN 2 AND 150),
 specialization TEXT NOT NULL CHECK(length(trim(specialization)) BETWEEN 2 AND 150),
 phone TEXT UNIQUE NOT NULL CHECK(length(phone) BETWEEN 11 AND 16 AND substr(phone,1,1)='+' AND substr(phone,2) NOT GLOB '*[^0-9]*'),
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

CREATE TABLE IF NOT EXISTS app_meta (
 key TEXT PRIMARY KEY,
 value TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date,appointment_time);
CREATE INDEX IF NOT EXISTS idx_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_records_diagnosis ON medical_records(diagnosis);
