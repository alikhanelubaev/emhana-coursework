-- Дәрігерлер жүктемесі · LEFT JOIN
-- Курстықтағы бөлім: 3.6.
SELECT d.id,d.full_name doctor_name,d.specialization,COUNT(a.id) count
FROM doctors d
LEFT
JOIN appointments a ON a.doctor_id=d.id
GROUP BY d.id
ORDER BY count DESC,d.full_name;
