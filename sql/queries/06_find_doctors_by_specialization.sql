-- Мамандығы бойынша дәрігер · WHERE
-- Курстықтағы бөлім: 3.5.
SELECT id,full_name,specialization,cabinet
FROM doctors
WHERE specialization=:specialization
ORDER BY id;
