-- Төрт кестедегі CREATE / READ / UPDATE / DELETE.
-- SAVEPOINT пен ROLLBACK демонстрация соңында бастапқы базаны сақтайды.
SAVEPOINT coursework_crud;

INSERT INTO patients(id, full_name, birth_date, gender, phone, address)
VALUES (900001, 'Тест Пациент', '2000-01-01', 'Ер', '+77000000001', 'Астана');

INSERT INTO doctors(id, full_name, specialization, phone, cabinet)
VALUES (900001, 'Тест Дәрігер', 'Терапевт', '+77000000002', 201);

INSERT INTO appointments(id, patient_id, doctor_id, appointment_date, appointment_time, reason)
VALUES (900001, 900001, 900001, '2026-09-20', '09:00', 'Алғашқы тексеру');

INSERT INTO medical_records(id, patient_id, record_date, diagnosis, complaint, recommendation)
VALUES (900001, 900001, '2026-09-20', 'Тест диагноз', 'Тест шағым', 'Қайта келу');

SELECT * FROM patients WHERE id = 900001;
SELECT * FROM doctors WHERE id = 900001;
SELECT * FROM appointments WHERE id = 900001;
SELECT * FROM medical_records WHERE id = 900001;

UPDATE patients SET address = 'Астана, Есіл ауданы' WHERE id = 900001;
UPDATE doctors SET cabinet = 202 WHERE id = 900001;
UPDATE appointments SET appointment_time = '10:30' WHERE id = 900001;
UPDATE medical_records SET recommendation = 'Жаңартылған ұсыныс' WHERE id = 900001;

SELECT p.full_name, p.address, d.cabinet, a.appointment_time, r.recommendation
FROM patients p
JOIN appointments a ON a.patient_id = p.id
JOIN doctors d ON d.id = a.doctor_id
JOIN medical_records r ON r.patient_id = p.id
WHERE p.id = 900001;

-- Алдымен тәуелді жазбалар, содан кейін негізгі кестелер жойылады.
DELETE FROM medical_records WHERE id = 900001;
DELETE FROM appointments WHERE id = 900001;
DELETE FROM doctors WHERE id = 900001;
DELETE FROM patients WHERE id = 900001;

SELECT COUNT(*) AS demo_patient_after_delete FROM patients WHERE id = 900001;
ROLLBACK TO coursework_crud;
RELEASE coursework_crud;
