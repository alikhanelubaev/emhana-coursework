-- Аты-жөнінің басы бойынша іздеу · LIKE
-- Курстықтағы бөлім: 3.5.
SELECT id,full_name,phone
FROM patients
WHERE full_name LIKE :prefix ESCAPE '\'
ORDER BY full_name;
