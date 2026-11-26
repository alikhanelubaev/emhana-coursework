-- Валидация Python-ға тәуелді емес: SQLite кез келген клиенттен қорғауды орындайды.
CREATE TRIGGER IF NOT EXISTS patients_birth_insert
BEFORE INSERT ON patients
WHEN NEW.birth_date > date('now', 'localtime')
BEGIN
    SELECT RAISE(ABORT, 'birth_future');
END;

CREATE TRIGGER IF NOT EXISTS patients_birth_update
BEFORE UPDATE OF birth_date ON patients
BEGIN
    SELECT RAISE(ABORT, 'birth_future')
    WHERE NEW.birth_date > date('now', 'localtime');
    SELECT RAISE(ABORT, 'birth_after_history')
    WHERE EXISTS (
        SELECT 1 FROM appointments
        WHERE patient_id = OLD.id AND appointment_date < NEW.birth_date
    ) OR EXISTS (
        SELECT 1 FROM medical_records
        WHERE patient_id = OLD.id AND record_date < NEW.birth_date
    );
END;

CREATE TRIGGER IF NOT EXISTS appointments_birth_insert
BEFORE INSERT ON appointments
WHEN NEW.appointment_date < (SELECT birth_date FROM patients WHERE id = NEW.patient_id)
BEGIN
    SELECT RAISE(ABORT, 'appointment_before_birth');
END;

CREATE TRIGGER IF NOT EXISTS appointments_birth_update
BEFORE UPDATE OF patient_id, appointment_date ON appointments
WHEN NEW.appointment_date < (SELECT birth_date FROM patients WHERE id = NEW.patient_id)
BEGIN
    SELECT RAISE(ABORT, 'appointment_before_birth');
END;

CREATE TRIGGER IF NOT EXISTS records_dates_insert
BEFORE INSERT ON medical_records
BEGIN
    SELECT RAISE(ABORT, 'record_future')
    WHERE NEW.record_date > date('now', 'localtime');
    SELECT RAISE(ABORT, 'record_before_birth')
    WHERE NEW.record_date < (SELECT birth_date FROM patients WHERE id = NEW.patient_id);
END;

CREATE TRIGGER IF NOT EXISTS records_dates_update
BEFORE UPDATE OF patient_id, record_date ON medical_records
BEGIN
    SELECT RAISE(ABORT, 'record_future')
    WHERE NEW.record_date > date('now', 'localtime');
    SELECT RAISE(ABORT, 'record_before_birth')
    WHERE NEW.record_date < (SELECT birth_date FROM patients WHERE id = NEW.patient_id);
END;
