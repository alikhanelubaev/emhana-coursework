-- Күн аралығындағы қабылдаулар · BETWEEN
-- Курстықтағы бөлім: 3.5.
SELECT id,patient_id,doctor_id,appointment_date,appointment_time,reason
FROM appointments
WHERE appointment_date BETWEEN :start_date AND :end_date
ORDER BY appointment_date,appointment_time;
