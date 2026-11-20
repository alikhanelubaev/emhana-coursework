"""Деректерді енгізу, өзгерту және жою функциялары."""

PATIENTS = [
    ("Айдос Нұрланов", "2004-03-12", "Ер", "87001234567", "Астана"),
    ("Аружан Серікқызы", "2003-07-25", "Әйел", "87007654321", "Астана"),
    ("Данияр Қасымов", "2005-11-08", "Ер", "87005556677", "Астана"),
    ("Мадина Ермекова", "2004-01-19", "Әйел", "87008889900", "Астана"),
    ("Нұрбек Әлиев", "2002-09-30", "Ер", "87001112233", "Астана"),
]

DOCTORS = [
    ("Ерлан Сейітов", "Терапевт", "87001112244", 101),
    ("Айгүл Мұратова", "Кардиолог", "87002223355", 102),
    ("Данияр Әбілов", "Невропатолог", "87003334466", 103),
    ("Гүлнар Қасымова", "Педиатр", "87004445577", 104),
    ("Марат Омаров", "Хирург", "87005556688", 105),
]

APPOINTMENTS = [
    (1, 1, "2026-09-10", "09:00", "Жалпы тексеру"),
    (2, 2, "2026-09-10", "10:30", "Жүрек тексеруі"),
    (3, 3, "2026-09-11", "11:00", "Бас ауруы"),
    (4, 4, "2026-09-11", "12:00", "Тексеру"),
    (5, 5, "2026-09-12", "14:00", "Жоспарлы тексеру"),
]

MEDICAL_RECORDS = [
    (1, "2026-09-10", "ЖРВИ", "Дене қызуы", "Демалу және сұйықтық ішу"),
    (2, "2026-09-10", "Гипертония", "Қан қысымы", "Дәрігер бақылауы"),
    (3, "2026-09-11", "Мигрень", "Бас ауруы", "Тексеруден өту"),
    (4, "2026-09-11", "ЖРВИ", "Жөтел", "Ем қабылдау"),
    (5, "2026-09-12", "Дені сау", "Шағым жоқ", "Жоспарлы бақылау"),
]


def insert_initial_data(conn):
    """Төрт кестеге бастапқы жолдарды executemany арқылы енгізеді."""
    with conn:
        conn.executemany(
            "INSERT INTO patients (full_name, birth_date, gender, phone, address) "
            "VALUES (?, ?, ?, ?, ?)", PATIENTS)
        conn.executemany(
            "INSERT INTO doctors (full_name, specialization, phone, cabinet) "
            "VALUES (?, ?, ?, ?)", DOCTORS)
        conn.executemany(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, "
            "appointment_time, reason) VALUES (?, ?, ?, ?, ?)", APPOINTMENTS)
        conn.executemany(
            "INSERT INTO medical_records (patient_id, record_date, diagnosis, "
            "complaint, recommendation) VALUES (?, ?, ?, ?, ?)", MEDICAL_RECORDS)


def add_patient(conn, full_name, birth_date, gender, phone, address):
    """Жаңа пациентті қосады және оның id нөмірін қайтарады."""
    with conn:
        cursor = conn.execute(
            "INSERT INTO patients (full_name, birth_date, gender, phone, address) "
            "VALUES (?, ?, ?, ?, ?)",
            (full_name, birth_date, gender, phone, address))
    return cursor.lastrowid


def add_doctor(conn, full_name, specialization, phone, cabinet):
    """Жаңа дәрігерді қосады."""
    with conn:
        cursor = conn.execute(
            "INSERT INTO doctors (full_name, specialization, phone, cabinet) "
            "VALUES (?, ?, ?, ?)",
            (full_name, specialization, phone, cabinet))
    return cursor.lastrowid


def add_appointment(conn, patient_id, doctor_id, date, time, reason):
    """Қабылдауды тіркейді."""
    with conn:
        cursor = conn.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, "
            "appointment_time, reason) VALUES (?, ?, ?, ?, ?)",
            (patient_id, doctor_id, date, time, reason))
    return cursor.lastrowid


def add_medical_record(conn, patient_id, date, diagnosis, complaint, recommendation):
    """Медициналық жазба қосады."""
    with conn:
        cursor = conn.execute(
            "INSERT INTO medical_records (patient_id, record_date, diagnosis, "
            "complaint, recommendation) VALUES (?, ?, ?, ?, ?)",
            (patient_id, date, diagnosis, complaint, recommendation))
    return cursor.lastrowid


def update_patient_address(conn, patient_id, new_address):
    """Пациенттің мекенжайын өзгертеді."""
    with conn:
        cursor = conn.execute(
            "UPDATE patients SET address = ? WHERE id = ?",
            (new_address, patient_id))
    return cursor.rowcount


def reschedule_appointment(conn, appointment_id, new_date, new_time):
    """Қабылдаудың күні мен уақытын ауыстырады."""
    with conn:
        cursor = conn.execute(
            "UPDATE appointments SET appointment_date = ?, appointment_time = ? "
            "WHERE id = ?", (new_date, new_time, appointment_id))
    return cursor.rowcount


def delete_appointment(conn, appointment_id):
    """Қабылдау жазбасын жояды."""
    with conn:
        cursor = conn.execute(
            "DELETE FROM appointments WHERE id = ?", (appointment_id,))
    return cursor.rowcount
