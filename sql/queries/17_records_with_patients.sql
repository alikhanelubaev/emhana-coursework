-- Диагноз бойынша пациенттер · JOIN WHERE
-- Курстықтағы бөлім: 3.6.
SELECT r.record_date,p.full_name patient_name,r.diagnosis,r.complaint,r.recommendation
FROM medical_records r
JOIN patients p ON p.id=r.patient_id
WHERE r.diagnosis=:diagnosis
ORDER BY r.record_date;
