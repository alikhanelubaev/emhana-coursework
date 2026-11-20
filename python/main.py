"""Қалалық емхана картотекасы: деректер базасын құру және өңдеу."""
import os
import sqlite3

import data
import queries
from database import DB_NAME, create_tables, get_connection


def count_rows(conn):
    """Әр кестедегі жазба санын шығарады."""
    for table in ("patients", "doctors", "appointments", "medical_records"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count}")


def list_tables(conn):
    """Базадағы кестелердің атауларын шығарады."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    for (name,) in rows:
        print(name)


def add_new_records(conn):
    """Базаға жаңа пациенттерді, дәрігерді, қабылдауларды және жазбаларды қосады."""
    data.add_patient(conn, "Әсел Бекова", "1985-05-14", "Әйел", "87009990011", "Астана")
    data.add_patient(conn, "Ерасыл Жақсылықов", "2018-02-03", "Ер", "87004443322", "Астана")
    data.add_patient(conn, "Гүлмира Тоқтарова", "1962-12-01", "Әйел", "87006667788", "Астана")
    data.add_doctor(conn, "Лаура Нұрмағамбетова", "Офтальмолог", "87006667799", 106)
    new_appointments = [
        (6, 1, "2026-09-14", "09:30", "Қан қысымын өлшеу"),
        (7, 4, "2026-09-14", "10:00", "Вакцинация"),
        (8, 2, "2026-09-15", "11:30", "Жүрек тұсындағы ауырсыну"),
        (1, 1, "2026-09-17", "09:00", "Қайта қарау"),
        (2, 2, "2026-09-18", "10:00", "Қайта қарау"),
        (6, 1, "2026-09-18", "15:00", "Қайта қарау"),
        (3, 3, "2026-09-19", "11:30", "Бас ауруын қайта тексеру"),
    ]
    for item in new_appointments:
        data.add_appointment(conn, *item)
    data.add_medical_record(conn, 6, "2026-09-14", "Гипертония",
                            "Қан қысымының көтерілуі", "Дәрігер бақылауы")
    data.add_medical_record(conn, 7, "2026-09-14", "Дені сау",
                            "Шағым жоқ", "Жоспарлы бақылау")
    data.add_medical_record(conn, 8, "2026-09-15", "Гипертония",
                            "Жүрек тұсындағы ауырсыну", "Кардиологқа қайта келу")
    data.add_medical_record(conn, 1, "2026-09-17", "ЖРВИ",
                            "Жөтел", "Ем қабылдау")
    data.add_medical_record(conn, 3, "2026-09-19", "Мигрень",
                            "Бас ауруы", "Невропатологтың бақылауы")


def update_demo(conn):
    """UPDATE операциясының нәтижесін алдыңғы және кейінгі күймен көрсетеді."""
    queries.show(conn, "SELECT id, full_name, address FROM patients WHERE id = 5")
    data.update_patient_address(conn, 5, "Астана, Сарыарқа ауданы")
    queries.show(conn, "SELECT id, full_name, address FROM patients WHERE id = 5")
    data.reschedule_appointment(conn, 5, "2026-09-13", "15:30")
    queries.show(conn, "SELECT id, appointment_date, appointment_time "
                       "FROM appointments WHERE id = 5")


def delete_demo(conn):
    """Қате қосылған қабылдауды жою мысалы."""
    wrong_id = data.add_appointment(conn, 5, 5, "2026-09-25", "10:00", "Қате жазба")
    print("Қосылған жазба id:", wrong_id)
    count_before = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    deleted = data.delete_appointment(conn, wrong_id)
    count_after = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    print("Жойылған жол саны:", deleted)
    print(f"Қабылдаулар саны: {count_before} -> {count_after}")


def check_integrity(conn):
    """Тұтастық шектеулерінің жұмысын тексереді."""
    tests = [
        ("Жоқ пациентке қабылдау қосу",
         lambda: data.add_appointment(conn, 999, 1, "2026-09-20", "09:00", "Тексеру")),
        ("Қабылдауы бар дәрігерді жою",
         lambda: conn.execute("DELETE FROM doctors WHERE id = 1")),
        ("Қайталанатын телефон нөмірі",
         lambda: data.add_patient(conn, "Тест Пациент", "2000-01-01", "Ер",
                                  "87001234567", "Астана")),
        ("Жыныс өрісіне қате мән",
         lambda: data.add_patient(conn, "Тест Пациент", "2000-01-01", "Белгісіз",
                                  "87000000000", "Астана")),
    ]
    for title, action in tests:
        try:
            action()
            print(f"{title}: операция орындалды")
        except sqlite3.IntegrityError as error:
            print(f"{title}:\n    қате -> {error}")


def main():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    conn = get_connection()

    print("--- Кестелерді құру ---")
    print("SQLite нұсқасы:", sqlite3.sqlite_version)
    create_tables(conn)
    list_tables(conn)

    print("--- Бастапқы деректерді енгізу ---")
    data.insert_initial_data(conn)
    count_rows(conn)

    print("--- Жаңа жазбаларды қосу (INSERT) ---")
    add_new_records(conn)
    count_rows(conn)

    print("--- Деректерді өзгерту (UPDATE) ---")
    update_demo(conn)

    print("--- Деректерді жою (DELETE) ---")
    delete_demo(conn)

    print("--- Тұтастық шектеулерін тексеру ---")
    check_integrity(conn)

    print("--- SELECT: барлық пациенттер ---")
    queries.select_all_patients(conn)

    print("--- SELECT: таңдалған бағандар ---")
    queries.select_columns(conn)

    print("--- SELECT: жасты есептеу ---")
    queries.select_with_age(conn)

    print("--- SELECT: DISTINCT ---")
    queries.select_distinct_diagnoses(conn)

    print("--- SELECT: агрегаттық функциялар ---")
    queries.select_patient_statistics(conn)

    print("--- WHERE: мамандық бойынша ---")
    queries.find_doctors_by_specialization(conn, "Терапевт")

    print("--- WHERE: LIKE ---")
    queries.search_patients_by_name(conn, "А")

    print("--- WHERE: BETWEEN ---")
    queries.appointments_between(conn, "2026-09-10", "2026-09-12")

    print("--- WHERE: AND ---")
    queries.women_born_before(conn, 2000)

    print("--- ORDER BY: туған күні ---")
    queries.patients_sorted_by_birth(conn)

    print("--- ORDER BY: DESC және LIMIT ---")
    queries.latest_appointments_first(conn)

    print("--- GROUP BY: жыныс ---")
    queries.patients_by_gender(conn)

    print("--- GROUP BY және HAVING: диагноз ---")
    queries.records_by_diagnosis(conn)

    print("--- JOIN: қабылдаулар тізімі ---")
    queries.appointment_list(conn)

    print("--- LEFT JOIN: дәрігерлердің жүктемесі ---")
    queries.doctor_workload(conn)

    print("--- JOIN және HAVING: жиі келетін пациенттер ---")
    queries.frequent_patients(conn)

    print("--- JOIN: диагноз бойынша жазбалар ---")
    queries.records_with_patients(conn, "Гипертония")

    print("--- Пациент картасы ---")
    queries.patient_card(conn, 1)

    conn.close()


if __name__ == "__main__":
    main()
