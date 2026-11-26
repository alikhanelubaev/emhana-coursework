-- Қайта келген пациенттер · JOIN GROUP BY HAVING
-- Курстықтағы бөлім: 3.6.
SELECT p.id,p.full_name patient_name,COUNT(a.id) visits
FROM patients p
JOIN appointments a ON a.patient_id=p.id
GROUP BY p.id
HAVING COUNT(a.id)>1
ORDER BY visits DESC,p.full_name;
