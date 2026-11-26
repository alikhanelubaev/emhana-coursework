-- Берілген жылға дейін туған әйелдер · AND
-- Курстықтағы бөлім: 3.5.
SELECT full_name,birth_date,gender
FROM patients
WHERE gender='Әйел' AND birth_date<:before_date
ORDER BY birth_date;
