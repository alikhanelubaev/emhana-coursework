-- Жазбалар саны бойынша диагноздар · HAVING
-- Курстықтағы бөлім: 3.5.
SELECT diagnosis,COUNT(*) count
FROM medical_records
GROUP BY diagnosis
HAVING COUNT(*)>=:minimum_count
ORDER BY count DESC,diagnosis;
