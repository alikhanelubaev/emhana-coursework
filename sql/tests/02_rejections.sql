-- expect-error белгілерін run.py оқиды. Қате шықпаса, тест құлайды.
-- SAVEPOINT ішінде RAISE(ABORT) тек қате операторды тоқтатады.
SAVEPOINT invalid_data;

-- expect-error: CHECK
INSERT INTO patients(full_name, birth_date, gender, phone, address)
VALUES (' ', '2000-01-01', 'Ер', '+77000000003', 'Астана');

-- expect-error: CHECK
INSERT INTO patients(full_name, birth_date, gender, phone, address)
VALUES ('Тест Пациент', '2026-02-30', 'Ер', '+77000000003', 'Астана');

-- expect-error: CHECK
INSERT INTO patients(full_name, birth_date, gender, phone, address)
VALUES ('Тест Пациент', '2000-01-01', 'Белгісіз', '+77000000003', 'Астана');

-- expect-error: CHECK
INSERT INTO patients(full_name, birth_date, gender, phone, address)
VALUES ('Тест Пациент', '2000-01-01', 'Ер', '+7abcd123456', 'Астана');

-- expect-error: UNIQUE
INSERT INTO patients(full_name, birth_date, gender, phone, address)
VALUES ('Тест Пациент', '2000-01-01', 'Ер', '+77001234567', 'Астана');

-- expect-error: birth_future
INSERT INTO patients(full_name, birth_date, gender, phone, address)
VALUES ('Тест Пациент', '2999-01-01', 'Ер', '+77000000003', 'Астана');

-- expect-error: FOREIGN KEY
INSERT INTO appointments(patient_id, doctor_id, appointment_date, appointment_time, reason)
VALUES (999, 1, '2026-10-01', '09:00', 'Тест');

-- expect-error: FOREIGN KEY
INSERT INTO appointments(patient_id, doctor_id, appointment_date, appointment_time, reason)
VALUES (1, 999, '2026-10-01', '09:00', 'Тест');

-- expect-error: appointments.doctor_id
INSERT INTO appointments(patient_id, doctor_id, appointment_date, appointment_time, reason)
VALUES (2, 1, '2026-09-10', '09:00', 'Тест');

-- expect-error: appointments.patient_id
INSERT INTO appointments(patient_id, doctor_id, appointment_date, appointment_time, reason)
VALUES (1, 2, '2026-09-10', '09:00', 'Тест');

-- expect-error: appointment_before_birth
INSERT INTO appointments(patient_id, doctor_id, appointment_date, appointment_time, reason)
VALUES (1, 1, '2000-01-01', '09:00', 'Тест');

-- expect-error: CHECK
INSERT INTO appointments(patient_id, doctor_id, appointment_date, appointment_time, reason)
VALUES (1, 1, '2026-10-01', '25:99', 'Тест');

-- expect-error: record_before_birth
INSERT INTO medical_records(patient_id, record_date, diagnosis, complaint, recommendation)
VALUES (1, '2000-01-01', 'Тест', 'Тест', 'Тест');

-- expect-error: record_future
INSERT INTO medical_records(patient_id, record_date, diagnosis, complaint, recommendation)
VALUES (1, '2999-01-01', 'Тест', 'Тест', 'Тест');

-- expect-error: FOREIGN KEY
INSERT INTO medical_records(patient_id, record_date, diagnosis, complaint, recommendation)
VALUES (999, '2026-09-20', 'Тест', 'Тест', 'Тест');

-- expect-error: CHECK
INSERT INTO medical_records(patient_id, record_date, diagnosis, complaint, recommendation)
VALUES (1, '2026-09-20', '', 'Тест', 'Тест');

-- expect-error: FOREIGN KEY
DELETE FROM patients WHERE id = 1;

-- expect-error: FOREIGN KEY
DELETE FROM doctors WHERE id = 1;

-- expect-error: birth_after_history
UPDATE patients SET birth_date = '2026-10-01' WHERE id = 1;

-- expect-error: appointment_before_birth
UPDATE appointments SET appointment_date = '2000-01-01' WHERE id = 1;

-- expect-error: record_before_birth
UPDATE medical_records SET record_date = '2000-01-01' WHERE id = 1;

-- expect-error: record_future
UPDATE medical_records SET record_date = '2999-01-01' WHERE id = 1;

-- expect-error: birth_future
UPDATE patients SET birth_date = '2999-01-01' WHERE id = 1;

-- expect-error: CHECK
UPDATE doctors SET cabinet = 0 WHERE id = 1;

-- expect-error: UNIQUE
UPDATE patients SET phone = '+77001234567' WHERE id = 2;

ROLLBACK TO invalid_data;
RELEASE invalid_data;

INSERT INTO test_assertions VALUES ('rejections kept patients', (SELECT COUNT(*) = 8 FROM patients));
INSERT INTO test_assertions VALUES ('rejections kept appointments', (SELECT COUNT(*) = 12 FROM appointments));
INSERT INTO test_assertions VALUES ('rejections kept records', (SELECT COUNT(*) = 10 FROM medical_records));
INSERT INTO test_assertions VALUES ('rejections kept FK', NOT EXISTS(SELECT 1 FROM pragma_foreign_key_check));
SELECT COUNT(*) AS passed_assertions FROM test_assertions;
