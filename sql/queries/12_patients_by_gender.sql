-- Жынысы бойынша пациент саны · GROUP BY
-- Курстықтағы бөлім: 3.5.
SELECT gender,COUNT(*) count
FROM patients
GROUP BY gender
ORDER BY gender;
