-- Берілген күндегі жас · есептелетін өріс
-- Курстықтағы бөлім: 3.4.
SELECT full_name,birth_date,CAST(strftime('%Y',:reference_date) AS INTEGER)-CAST(strftime('%Y',birth_date) AS INTEGER)-(strftime('%m-%d',:reference_date)<strftime('%m-%d',birth_date)) AS age
FROM patients
ORDER BY id;
