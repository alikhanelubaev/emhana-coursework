-- Сақталған есептер: DB Browser ішінде Views тізімінен ашылады.
CREATE VIEW IF NOT EXISTS v_patient_overview AS
SELECT
    p.id,
    p.full_name,
    p.birth_date,
    p.gender,
    p.phone,
    p.address,
    CAST(strftime('%Y', 'now', 'localtime') AS INTEGER)
        - CAST(strftime('%Y', p.birth_date) AS INTEGER)
        - (strftime('%m-%d', 'now', 'localtime') < strftime('%m-%d', p.birth_date)) AS age,
    (SELECT COUNT(*) FROM appointments a WHERE a.patient_id = p.id) AS visits,
    (SELECT COUNT(*) FROM medical_records r WHERE r.patient_id = p.id) AS records
FROM patients p;

CREATE VIEW IF NOT EXISTS v_appointments AS
SELECT
    a.id, a.appointment_date, a.appointment_time,
    a.patient_id, p.full_name AS patient_name,
    a.doctor_id, d.full_name AS doctor_name, d.specialization, a.reason
FROM appointments a
JOIN patients p ON p.id = a.patient_id
JOIN doctors d ON d.id = a.doctor_id;

CREATE VIEW IF NOT EXISTS v_doctor_workload AS
SELECT d.id, d.full_name AS doctor_name, d.specialization, COUNT(a.id) AS visits
FROM doctors d
LEFT JOIN appointments a ON a.doctor_id = d.id
GROUP BY d.id, d.full_name, d.specialization;

CREATE VIEW IF NOT EXISTS v_diagnoses AS
SELECT diagnosis, COUNT(*) AS records, COUNT(DISTINCT patient_id) AS patients
FROM medical_records
GROUP BY diagnosis;

CREATE VIEW IF NOT EXISTS v_frequent_patients AS
SELECT p.id, p.full_name AS patient_name, COUNT(a.id) AS visits
FROM patients p
JOIN appointments a ON a.patient_id = p.id
GROUP BY p.id, p.full_name
HAVING COUNT(a.id) > 1;

CREATE VIEW IF NOT EXISTS v_daily_appointments AS
SELECT appointment_date, COUNT(*) AS visits, COUNT(DISTINCT doctor_id) AS doctors
FROM appointments
GROUP BY appointment_date;
