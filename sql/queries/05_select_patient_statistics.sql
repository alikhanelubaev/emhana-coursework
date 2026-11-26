-- Пациенттер статистикасы · COUNT MIN MAX
-- Курстықтағы бөлім: 3.4.
SELECT COUNT(*) total,MIN(birth_date) oldest,MAX(birth_date) youngest
FROM patients;
