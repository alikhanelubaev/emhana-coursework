"""SQL сұраныстары және нәтижені кесте түрінде шығару."""

REFERENCE_DATE = "2026-10-01"


def show(conn, sql, params=()):
    """Сұранысты орындап, нәтижені консольге кесте түрінде шығарады."""
    cursor = conn.execute(sql, params)
    headers = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    cells = [["NULL" if v is None else str(v) for v in row] for row in rows]
    widths = [max([len(h)] + [len(row[i]) for row in cells])
              for i, h in enumerate(headers)]
    print(" | ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("-+-".join("-" * w for w in widths))
    for row in cells:
        print(" | ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"Жол саны: {len(rows)}")
    return rows


def select_all_patients(conn):
    return show(conn, "SELECT * FROM patients")


def select_columns(conn):
    return show(conn, "SELECT full_name, phone FROM patients")


def select_with_age(conn):
    sql = """
        SELECT full_name, birth_date,
               CAST((julianday(?) - julianday(birth_date)) / 365.25 AS INTEGER) AS age
        FROM patients
    """
    return show(conn, sql, (REFERENCE_DATE,))


def select_distinct_diagnoses(conn):
    return show(conn, "SELECT DISTINCT diagnosis FROM medical_records")


def select_patient_statistics(conn):
    sql = """
        SELECT COUNT(*) AS total,
               MIN(birth_date) AS oldest,
               MAX(birth_date) AS youngest
        FROM patients
    """
    return show(conn, sql)


def find_doctors_by_specialization(conn, specialization):
    sql = "SELECT id, full_name, cabinet FROM doctors WHERE specialization = ?"
    return show(conn, sql, (specialization,))


def search_patients_by_name(conn, prefix):
    sql = "SELECT id, full_name, phone FROM patients WHERE full_name LIKE ?"
    return show(conn, sql, (prefix + "%",))


def appointments_between(conn, start_date, end_date):
    sql = """
        SELECT id, patient_id, doctor_id, appointment_date, appointment_time
        FROM appointments
        WHERE appointment_date BETWEEN ? AND ?
    """
    return show(conn, sql, (start_date, end_date))


def women_born_before(conn, year):
    sql = """
        SELECT full_name, birth_date, gender
        FROM patients
        WHERE gender = 'Әйел' AND birth_date < ?
    """
    return show(conn, sql, (f"{year}-01-01",))


def patients_sorted_by_birth(conn):
    sql = "SELECT full_name, birth_date FROM patients ORDER BY birth_date ASC"
    return show(conn, sql)


def latest_appointments_first(conn):
    sql = """
        SELECT id, appointment_date, appointment_time, reason
        FROM appointments
        ORDER BY appointment_date DESC, appointment_time DESC
        LIMIT 5
    """
    return show(conn, sql)


def patients_by_gender(conn):
    sql = "SELECT gender, COUNT(*) AS cnt FROM patients GROUP BY gender"
    return show(conn, sql)


def records_by_diagnosis(conn):
    sql = """
        SELECT diagnosis, COUNT(*) AS cnt
        FROM medical_records
        GROUP BY diagnosis
        HAVING COUNT(*) >= 3
        ORDER BY cnt DESC, diagnosis
    """
    return show(conn, sql)


def appointment_list(conn):
    sql = """
        SELECT a.id, a.appointment_date AS date, a.appointment_time AS time,
               p.full_name AS patient, d.full_name AS doctor,
               d.specialization AS specialty
        FROM appointments AS a
        JOIN patients AS p ON p.id = a.patient_id
        JOIN doctors  AS d ON d.id = a.doctor_id
        ORDER BY a.appointment_date, a.appointment_time
    """
    return show(conn, sql)


def doctor_workload(conn):
    sql = """
        SELECT d.full_name AS doctor, d.specialization AS specialty,
               COUNT(a.id) AS appointments
        FROM doctors AS d
        LEFT JOIN appointments AS a ON a.doctor_id = d.id
        GROUP BY d.id
        ORDER BY appointments DESC, d.full_name
    """
    return show(conn, sql)


def frequent_patients(conn):
    sql = """
        SELECT p.full_name AS patient, COUNT(a.id) AS visits
        FROM patients AS p
        JOIN appointments AS a ON a.patient_id = p.id
        GROUP BY p.id
        HAVING COUNT(a.id) > 1
        ORDER BY visits DESC, p.full_name
    """
    return show(conn, sql)


def records_with_patients(conn, diagnosis):
    sql = """
        SELECT r.record_date AS date, p.full_name AS patient,
               r.diagnosis, r.recommendation
        FROM medical_records AS r
        JOIN patients AS p ON p.id = r.patient_id
        WHERE r.diagnosis = ?
        ORDER BY r.record_date
    """
    return show(conn, sql, (diagnosis,))


def patient_card(conn, patient_id):
    """Пациенттің толық картасын шығарады: жеке мәліметтер, қабылдаулар, жазбалар."""
    print("Жеке мәліметтер:")
    show(conn, "SELECT id, full_name, birth_date, phone FROM patients WHERE id = ?",
         (patient_id,))
    print("\nҚабылдаулар:")
    show(conn, """
        SELECT a.appointment_date AS date, a.appointment_time AS time,
               d.full_name AS doctor, a.reason
        FROM appointments AS a
        JOIN doctors AS d ON d.id = a.doctor_id
        WHERE a.patient_id = ?
        ORDER BY a.appointment_date, a.appointment_time
    """, (patient_id,))
    print("\nМедициналық жазбалар:")
    show(conn, """
        SELECT record_date AS date, diagnosis, recommendation
        FROM medical_records
        WHERE patient_id = ?
        ORDER BY record_date
    """, (patient_id,))
