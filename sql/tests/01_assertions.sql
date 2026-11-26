-- CHECK(ok=1) қате нәтижеде тестті бірден тоқтатады.
CREATE TEMP TABLE test_assertions (
    name TEXT PRIMARY KEY,
    ok INTEGER NOT NULL CHECK(ok = 1)
);

INSERT INTO test_assertions VALUES ('patients = 8', (SELECT COUNT(*) = 8 FROM patients));
INSERT INTO test_assertions VALUES ('doctors = 6', (SELECT COUNT(*) = 6 FROM doctors));
INSERT INTO test_assertions VALUES ('appointments = 12', (SELECT COUNT(*) = 12 FROM appointments));
INSERT INTO test_assertions VALUES ('medical_records = 10', (SELECT COUNT(*) = 10 FROM medical_records));
INSERT INTO test_assertions VALUES ('gender female = 4', (SELECT COUNT(*) = 4 FROM patients WHERE gender = 'Әйел'));
INSERT INTO test_assertions VALUES ('gender male = 4', (SELECT COUNT(*) = 4 FROM patients WHERE gender = 'Ер'));
INSERT INTO test_assertions VALUES ('distinct diagnoses = 4', (SELECT COUNT(DISTINCT diagnosis) = 4 FROM medical_records));
INSERT INTO test_assertions VALUES ('oldest patient', (SELECT full_name = 'Гүлмира Тоқтарова' FROM patients ORDER BY birth_date LIMIT 1));
INSERT INTO test_assertions VALUES ('women before 2000 = 2', (SELECT COUNT(*) = 2 FROM patients WHERE gender = 'Әйел' AND birth_date < '2000-01-01'));
INSERT INTO test_assertions VALUES ('appointments BETWEEN = 4', (SELECT COUNT(*) = 4 FROM appointments WHERE appointment_date BETWEEN '2026-09-10' AND '2026-09-12'));
INSERT INTO test_assertions VALUES ('latest appointment', (SELECT id = 12 FROM appointments ORDER BY appointment_date DESC, appointment_time DESC LIMIT 1));
INSERT INTO test_assertions VALUES ('JOIN visits = 12', (SELECT COUNT(*) = 12 FROM v_appointments));
INSERT INTO test_assertions VALUES ('LEFT JOIN preserves 6 doctors', (SELECT COUNT(*) = 6 FROM v_doctor_workload));
INSERT INTO test_assertions VALUES ('no visits doctor', (SELECT visits = 0 FROM v_doctor_workload WHERE id = 6));
INSERT INTO test_assertions VALUES ('busiest doctor', (SELECT visits = 4 FROM v_doctor_workload WHERE id = 1));
INSERT INTO test_assertions VALUES ('HAVING diagnoses = 2', (SELECT COUNT(*) = 2 FROM v_diagnoses WHERE records >= 3));
INSERT INTO test_assertions VALUES ('frequent patients = 4', (SELECT COUNT(*) = 4 FROM v_frequent_patients));
INSERT INTO test_assertions VALUES ('hypertension patients = 3', (SELECT patients = 3 FROM v_diagnoses WHERE diagnosis = 'Гипертония'));
INSERT INTO test_assertions VALUES ('overview patients = 8', (SELECT COUNT(*) = 8 FROM v_patient_overview));
INSERT INTO test_assertions VALUES ('patient card visits = 2', (SELECT visits = 2 FROM v_patient_overview WHERE id = 1));
INSERT INTO test_assertions VALUES ('patient card records = 2', (SELECT records = 2 FROM v_patient_overview WHERE id = 1));
INSERT INTO test_assertions VALUES ('updated patient address', (SELECT address = 'Астана, Сарыарқа ауданы' FROM patients WHERE id = 5));
INSERT INTO test_assertions VALUES ('updated appointment', (SELECT appointment_date = '2026-09-13' AND appointment_time = '15:30' FROM appointments WHERE id = 5));
INSERT INTO test_assertions VALUES ('CRUD patient rollback', (SELECT COUNT(*) = 0 FROM patients WHERE id = 900001));
INSERT INTO test_assertions VALUES ('CRUD doctor rollback', (SELECT COUNT(*) = 0 FROM doctors WHERE id = 900001));
INSERT INTO test_assertions VALUES ('CRUD appointment rollback', (SELECT COUNT(*) = 0 FROM appointments WHERE id = 900001));
INSERT INTO test_assertions VALUES ('CRUD record rollback', (SELECT COUNT(*) = 0 FROM medical_records WHERE id = 900001));
INSERT INTO test_assertions VALUES ('foreign keys enabled', (SELECT foreign_keys = 1 FROM pragma_foreign_keys));
INSERT INTO test_assertions VALUES ('no FK errors', NOT EXISTS(SELECT 1 FROM pragma_foreign_key_check));
INSERT INTO test_assertions VALUES ('integrity ok', (SELECT integrity_check = 'ok' FROM pragma_integrity_check));

-- ON UPDATE CASCADE өзгерісті екі тәуелді кестеге жеткізеді.
UPDATE patients SET id = 101 WHERE id = 1;
INSERT INTO test_assertions VALUES ('cascade patient visits', (SELECT COUNT(*) = 2 FROM appointments WHERE patient_id = 101));
INSERT INTO test_assertions VALUES ('cascade patient records', (SELECT COUNT(*) = 2 FROM medical_records WHERE patient_id = 101));
UPDATE patients SET id = 1 WHERE id = 101;

UPDATE doctors SET id = 101 WHERE id = 1;
INSERT INTO test_assertions VALUES ('cascade doctor visits', (SELECT COUNT(*) = 4 FROM appointments WHERE doctor_id = 101));
UPDATE doctors SET id = 1 WHERE id = 101;

SELECT name, ok FROM test_assertions ORDER BY name;
SELECT COUNT(*) AS passed_assertions FROM test_assertions;
