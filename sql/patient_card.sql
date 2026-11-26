-- Толық карта: :patient_id параметрімен үш байланысты нәтиже.
SELECT id, full_name, birth_date, gender, phone, address
FROM patients
WHERE id = :patient_id;

SELECT a.appointment_date, a.appointment_time, d.full_name AS doctor,
       d.specialization, a.reason
FROM appointments a
JOIN doctors d ON d.id = a.doctor_id
WHERE a.patient_id = :patient_id
ORDER BY a.appointment_date, a.appointment_time;

SELECT record_date, diagnosis, complaint, recommendation
FROM medical_records
WHERE patient_id = :patient_id
ORDER BY record_date, id;
