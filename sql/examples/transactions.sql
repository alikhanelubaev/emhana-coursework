-- Бірнеше байланысты өзгерісті біртұтас операция ретінде орындау.
SAVEPOINT address_change;
UPDATE patients SET address = 'Уақытша мекенжай' WHERE id = 5;
SELECT id, full_name, address FROM patients WHERE id = 5;
ROLLBACK TO address_change;
RELEASE address_change;

-- Өзгеріс қайтарылған: курстықтағы мекенжай сақталады.
SELECT id, full_name, address FROM patients WHERE id = 5;

-- SQLite query planner қолданылатын индексті көрсетеді.
EXPLAIN QUERY PLAN
SELECT id, appointment_date, appointment_time
FROM appointments
WHERE patient_id = 1;

PRAGMA foreign_key_check;
PRAGMA integrity_check;
