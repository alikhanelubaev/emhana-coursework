-- Толық қабылдау тізімі · үш кесте JOIN
-- Курстықтағы бөлім: 3.6.
SELECT a.id,a.appointment_date,a.appointment_time,p.full_name patient_name,d.full_name doctor_name,d.specialization,a.reason
FROM appointments a
JOIN patients p ON p.id=a.patient_id
JOIN doctors d ON d.id=a.doctor_id
ORDER BY a.appointment_date,a.appointment_time;
