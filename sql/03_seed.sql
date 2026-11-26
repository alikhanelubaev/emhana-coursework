-- Соңғы курстықтағы 8/6/12/10 жазба. Қайта орындау өзгертілген базаны тазаламайды.
BEGIN IMMEDIATE;

WITH initial(id, full_name, birth_date, gender, phone, address) AS (
 VALUES
    (1, 'Айдос Нұрланов', '2004-03-12', 'Ер', '+77001234567', 'Астана'),
    (2, 'Аружан Серікқызы', '2003-07-25', 'Әйел', '+77007654321', 'Астана'),
    (3, 'Данияр Қасымов', '2005-11-08', 'Ер', '+77005556677', 'Астана'),
    (4, 'Мадина Ермекова', '2004-01-19', 'Әйел', '+77008889900', 'Астана'),
    (5, 'Нұрбек Әлиев', '2002-09-30', 'Ер', '+77001112233', 'Астана, Сарыарқа ауданы'),
    (6, 'Әсел Бекова', '1985-05-14', 'Әйел', '+77009990011', 'Астана'),
    (7, 'Ерасыл Жақсылықов', '2018-02-03', 'Ер', '+77004443322', 'Астана'),
    (8, 'Гүлмира Тоқтарова', '1962-12-01', 'Әйел', '+77006667788', 'Астана')
)
INSERT INTO patients(id, full_name, birth_date, gender, phone, address)
SELECT id, full_name, birth_date, gender, phone, address FROM initial
WHERE NOT EXISTS (SELECT 1 FROM app_meta WHERE key = 'seeded');

WITH initial(id, full_name, specialization, phone, cabinet) AS (
 VALUES
    (1, 'Ерлан Сейітов', 'Терапевт', '+77001112244', 101),
    (2, 'Айгүл Мұратова', 'Кардиолог', '+77002223355', 102),
    (3, 'Данияр Әбілов', 'Невропатолог', '+77003334466', 103),
    (4, 'Гүлнар Қасымова', 'Педиатр', '+77004445577', 104),
    (5, 'Марат Омаров', 'Хирург', '+77005556688', 105),
    (6, 'Лаура Нұрмағамбетова', 'Офтальмолог', '+77006667799', 106)
)
INSERT INTO doctors(id, full_name, specialization, phone, cabinet)
SELECT id, full_name, specialization, phone, cabinet FROM initial
WHERE NOT EXISTS (SELECT 1 FROM app_meta WHERE key = 'seeded');

WITH initial(id, patient_id, doctor_id, appointment_date, appointment_time, reason) AS (
 VALUES
    (1, 1, 1, '2026-09-10', '09:00', 'Жалпы тексеру'),
    (2, 2, 2, '2026-09-10', '10:30', 'Жүрек тексеруі'),
    (3, 3, 3, '2026-09-11', '11:00', 'Бас ауруы'),
    (4, 4, 4, '2026-09-11', '12:00', 'Тексеру'),
    (5, 5, 5, '2026-09-13', '15:30', 'Жоспарлы тексеру'),
    (6, 6, 1, '2026-09-14', '09:30', 'Қан қысымын өлшеу'),
    (7, 7, 4, '2026-09-14', '10:00', 'Вакцинация'),
    (8, 8, 2, '2026-09-15', '11:30', 'Жүрек тұсындағы ауырсыну'),
    (9, 1, 1, '2026-09-17', '09:00', 'Қайта қарау'),
    (10, 2, 2, '2026-09-18', '10:00', 'Қайта қарау'),
    (11, 6, 1, '2026-09-18', '15:00', 'Қайта қарау'),
    (12, 3, 3, '2026-09-19', '11:30', 'Бас ауруын қайта тексеру')
)
INSERT INTO appointments(id, patient_id, doctor_id, appointment_date, appointment_time, reason)
SELECT id, patient_id, doctor_id, appointment_date, appointment_time, reason FROM initial
WHERE NOT EXISTS (SELECT 1 FROM app_meta WHERE key = 'seeded');

WITH initial(id, patient_id, record_date, diagnosis, complaint, recommendation) AS (
 VALUES
    (1, 1, '2026-09-10', 'ЖРВИ', 'Дене қызуы', 'Демалу және сұйықтық ішу'),
    (2, 2, '2026-09-10', 'Гипертония', 'Қан қысымы', 'Дәрігер бақылауы'),
    (3, 3, '2026-09-11', 'Мигрень', 'Бас ауруы', 'Тексеруден өту'),
    (4, 4, '2026-09-11', 'ЖРВИ', 'Жөтел', 'Ем қабылдау'),
    (5, 5, '2026-09-12', 'Дені сау', 'Шағым жоқ', 'Жоспарлы бақылау'),
    (6, 6, '2026-09-14', 'Гипертония', 'Қан қысымының көтерілуі', 'Дәрігер бақылауы'),
    (7, 7, '2026-09-14', 'Дені сау', 'Шағым жоқ', 'Жоспарлы бақылау'),
    (8, 8, '2026-09-15', 'Гипертония', 'Жүрек тұсындағы ауырсыну', 'Кардиологқа қайта келу'),
    (9, 1, '2026-09-17', 'ЖРВИ', 'Жөтел', 'Ем қабылдау'),
    (10, 3, '2026-09-19', 'Мигрень', 'Бас ауруы', 'Невропатологтың бақылауы')
)
INSERT INTO medical_records(id, patient_id, record_date, diagnosis, complaint, recommendation)
SELECT id, patient_id, record_date, diagnosis, complaint, recommendation FROM initial
WHERE NOT EXISTS (SELECT 1 FROM app_meta WHERE key = 'seeded');

INSERT OR IGNORE INTO app_meta VALUES ('seeded', '1');
COMMIT;
