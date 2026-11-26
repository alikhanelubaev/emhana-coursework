-- Соңғы бес қабылдау · DESC LIMIT
-- Курстықтағы бөлім: 3.5.
SELECT id,appointment_date,appointment_time,reason
FROM appointments
ORDER BY appointment_date DESC,appointment_time DESC
LIMIT 5;
