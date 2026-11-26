"""Транзакциялар, рөлдер, CRUD, кіру және әрекеттер журналы."""
from datetime import datetime, timedelta, timezone
import re
import sqlite3
import tempfile
from pathlib import Path
from database import connection, database_path, fold
from errors import AccessError, LoginError, NotFoundError, ValidationError
from models import ENTITIES, ROLES, WRITE_PERMISSIONS
from security import hash_password, verify_password
from validation import entity_data, positive_id, text


def can_write(user: dict, entity: str) -> bool:
    return entity in WRITE_PERMISSIONS.get(user.get("role"), frozenset())


def _audit(conn, actor, action, entity, record_id=None, details=""):
    conn.execute("INSERT INTO audit_log(user_id,action,entity,record_id,details) VALUES (?,?,?,?,?)",
                 (actor, action, entity, record_id, details))


def _require(conn, actor, entity=None, admin=False):
    row = conn.execute("SELECT id,username,display_name,role,active FROM users WHERE id=?", (actor,)).fetchone()
    if row is None or not row["active"]:
        raise AccessError("Жүйеге қайта кіріңіз.")
    user = dict(row)
    if (admin and user["role"] != "admin") or (entity and not can_write(user, entity)):
        raise AccessError("Бұл әрекетке рұқсатыңыз жоқ.")
    return user


def _integrity_message(error):
    message = str(error)
    if "phone" in message:
        return "Бұл телефон нөмірі бұрын тіркелген."
    if "appointments.doctor_id" in message:
        return "Дәрігердің осы күн мен уақыты бос емес. Басқа уақыт таңдаңыз."
    if "appointments.patient_id" in message:
        return "Пациент осы уақытта басқа қабылдауға жазылған."
    if "FOREIGN KEY" in message:
        return "Байланысты жазбалар бар немесе таңдалған пациент/дәрігер табылмады."
    if "username" in message:
        return "Бұл логин бұрын тіркелген."
    return "Енгізілген мәлімет деректер базасының талаптарына сәйкес емес."


class ClinicService:
    def __init__(self, db_path=None):
        self.path = database_path(db_path)

    def read(self, sql, params=()):
        with connection(self.path) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def user(self, user_id):
        rows = self.read("SELECT id,username,display_name,role,active FROM users WHERE id=? AND active=1", (user_id,))
        return rows[0] if rows else None

    def authenticate(self, username, password):
        now = datetime.now(timezone.utc)
        rows = self.read("SELECT * FROM users WHERE username=? COLLATE NOCASE", (str(username).strip(),))
        user = rows[0] if rows else None
        if user and user["locked_until"] and datetime.fromisoformat(user["locked_until"]) > now:
            raise LoginError("Кіру уақытша шектелді. Бес минуттан кейін қайталаңыз.")
        valid = user and user["active"] and verify_password(password, user["password_hash"])
        with connection(self.path) as conn:
            if valid:
                conn.execute("UPDATE users SET failed_attempts=0,locked_until=NULL WHERE id=?", (user["id"],))
                _audit(conn, user["id"], "Кіру", "users", user["id"], "Жүйеге сәтті кірді")
            elif user:
                attempts = user["failed_attempts"] + 1
                locked = (now + timedelta(minutes=5)).isoformat() if attempts >= 5 else None
                conn.execute("UPDATE users SET failed_attempts=?,locked_until=? WHERE id=?", (0 if locked else attempts, locked, user["id"]))
                _audit(conn, user["id"], "Кіру қатесі", "users", user["id"], "Кіру деректері қабылданбады")
        if not valid:
            raise LoginError("Логин немесе құпиясөз қате.")
        return self.user(user["id"])

    def get(self, entity, record_id):
        if entity not in ENTITIES:
            raise ValidationError("Белгісіз кесте.")
        rows = self.read(f"SELECT * FROM {entity} WHERE id=?", (positive_id(record_id),))
        if not rows:
            raise NotFoundError("Жазба табылмады. Тізімді жаңартыңыз.")
        return rows[0]

    def list_records(self, entity, search="", filters=None, sort="id", descending=False):
        if entity not in ENTITIES or sort not in ENTITIES[entity].sort_fields:
            raise ValidationError("Кесте немесе сұрыптау өрісі қате.")
        filters = filters or {}
        prefix = {"patients":"p", "doctors":"d", "appointments":"a", "medical_records":"r"}[entity]
        selects = {
            "patients": "SELECT p.* FROM patients p",
            "doctors": "SELECT d.* FROM doctors d",
            "appointments": "SELECT a.*,p.full_name patient_name,d.full_name doctor_name,d.specialization FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id",
            "medical_records": "SELECT r.*,p.full_name patient_name FROM medical_records r JOIN patients p ON p.id=r.patient_id",
        }
        search_fields = {
            "patients":["p.full_name","p.phone","p.address"],
            "doctors":["d.full_name","d.specialization","d.phone","CAST(d.cabinet AS TEXT)"],
            "appointments":["p.full_name","d.full_name","a.reason"],
            "medical_records":["p.full_name","r.diagnosis","r.complaint","r.recommendation"],
        }
        clauses, params = [], []
        if search.strip():
            # instr treats SQL wildcard characters as literal text and supports Unicode via casefold.
            clauses.append("(" + " OR ".join(f"instr(casefold({field}),?)>0" for field in search_fields[entity]) + ")")
            params.extend([fold(search.strip())] * len(search_fields[entity]))
        allowed_filters = {"patients":{"gender"}, "doctors":{"specialization"}, "appointments":{"doctor_id","patient_id"}, "medical_records":{"patient_id","diagnosis"}}
        for key, value in filters.items():
            if value is None or value == "":
                continue
            if key in allowed_filters[entity]:
                clauses.append(f"{prefix}.{key}=?")
                params.append(value)
            elif key in {"start_date", "end_date"} and entity in {"appointments", "medical_records"}:
                field = "appointment_date" if entity == "appointments" else "record_date"
                clauses.append(f"{prefix}.{field} {'>=' if key=='start_date' else '<='} ?")
                params.append(value)
            else:
                raise ValidationError("Белгісіз сүзгі.")
        if filters.get("start_date") and filters.get("end_date") and filters["start_date"] > filters["end_date"]:
            raise ValidationError("Басталу күні аяқталу күнінен кейін болмауы керек.")
        sql = selects[entity] + (" WHERE " + " AND ".join(clauses) if clauses else "")
        sql += f" ORDER BY {prefix}.{sort} {'DESC' if descending else 'ASC'}, {prefix}.id"
        return self.read(sql, params)

    def save(self, entity, values, actor_id, record_id=None):
        data = entity_data(entity, values)
        if record_id is not None:
            record_id = positive_id(record_id)
        try:
            with connection(self.path) as conn:
                _require(conn, actor_id, entity)
                if record_id and not conn.execute(f"SELECT 1 FROM {entity} WHERE id=?", (record_id,)).fetchone():
                    raise NotFoundError("Бұл жазба басқа терезеде жойылған. Тізімді жаңартыңыз.")
                if entity == "patients" and record_id:
                    earliest = conn.execute("SELECT MIN(day) FROM (SELECT appointment_date day FROM appointments WHERE patient_id=? UNION ALL SELECT record_date FROM medical_records WHERE patient_id=?)", (record_id,record_id)).fetchone()[0]
                    if earliest and data["birth_date"] > earliest:
                        raise ValidationError("Туған күн пациенттің бұрынғы қабылдауынан немесе жазбасынан кейін болмауы керек.")
                if "patient_id" in data:
                    patient = conn.execute("SELECT birth_date FROM patients WHERE id=?", (data["patient_id"],)).fetchone()
                    if patient is None:
                        raise ValidationError("Пациент табылмады.")
                    visit_date = data.get("appointment_date", data.get("record_date"))
                    if visit_date < patient["birth_date"]:
                        raise ValidationError("Жазба күні пациенттің туған күнінен бұрын болмауы керек.")
                if entity == "appointments" and not conn.execute("SELECT 1 FROM doctors WHERE id=?", (data["doctor_id"],)).fetchone():
                    raise ValidationError("Дәрігер табылмады.")
                fields = ENTITIES[entity].fields
                if record_id:
                    conn.execute(f"UPDATE {entity} SET " + ",".join(f"{field}=?" for field in fields) + " WHERE id=?", (*[data[f] for f in fields],record_id))
                    action = "Өзгерту"
                else:
                    cursor = conn.execute(f"INSERT INTO {entity} (" + ",".join(fields) + ") VALUES (" + ",".join("?" for _ in fields) + ")", [data[f] for f in fields])
                    record_id = cursor.lastrowid
                    action = "Қосу"
                _audit(conn, actor_id, action, entity, record_id, ENTITIES[entity].singular + " сақталды")
            return record_id
        except sqlite3.IntegrityError as error:
            raise ValidationError(_integrity_message(error)) from None

    def delete(self, entity, record_id, actor_id):
        if entity not in ENTITIES:
            raise ValidationError("Белгісіз кесте.")
        record_id = positive_id(record_id)
        try:
            with connection(self.path) as conn:
                _require(conn, actor_id, entity)
                cursor = conn.execute(f"DELETE FROM {entity} WHERE id=?", (record_id,))
                if cursor.rowcount != 1:
                    raise NotFoundError("Жойылатын жазба табылмады.")
                _audit(conn, actor_id, "Жою", entity, record_id, "Жазба жойылды")
        except sqlite3.IntegrityError:
            raise ValidationError("Бұл жазбаға қабылдаулар немесе медициналық жазбалар байланысқан. Алдымен байланысты жазбаларды қараңыз.") from None

    def patient_card(self, patient_id):
        patient_id = positive_id(patient_id)
        return {
            "patient": self.get("patients", patient_id),
            "appointments": self.list_records("appointments", filters={"patient_id":patient_id}, sort="appointment_date", descending=True),
            "records": self.list_records("medical_records", filters={"patient_id":patient_id}, sort="record_date", descending=True),
        }

    def counts(self):
        with connection(self.path) as conn:
            return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ENTITIES}

    def list_users(self, actor_id):
        with connection(self.path) as conn:
            _require(conn, actor_id, admin=True)
            return [dict(r) for r in conn.execute("SELECT id,username,display_name,role,active,created_at FROM users ORDER BY id")]

    def save_user(self, actor_id, username, display_name, role, password="", active=True, record_id=None):
        username = str(username).strip().lower()
        if not re.fullmatch(r"[a-z0-9_.-]{3,40}", username):
            raise ValidationError("Логин 3–40 латын әрпі, сан, нүкте, сызықша немесе _ таңбасынан тұрсын.")
        display_name = text(display_name, "Қызметкер", maximum=150)
        if role not in ROLES:
            raise ValidationError("Рөлді тізімнен таңдаңыз.")
        if (not record_id or password) and not 8 <= len(password) <= 128:
            raise ValidationError("Құпиясөз ұзындығы 8–128 таңба болуы керек.")
        try:
            with connection(self.path) as conn:
                _require(conn, actor_id, admin=True)
                if record_id:
                    previous = conn.execute("SELECT * FROM users WHERE id=?", (record_id,)).fetchone()
                    if previous is None:
                        raise NotFoundError("Қызметкер табылмады.")
                    if int(record_id) == actor_id and (not active or role != "admin"):
                        raise ValidationError("Өз әкімші рөліңізді өшіруге болмайды.")
                    if previous["role"] == "admin" and previous["active"] and (not active or role != "admin"):
                        count = conn.execute("SELECT COUNT(*) FROM users WHERE active=1 AND role='admin'").fetchone()[0]
                        if count <= 1:
                            raise ValidationError("Кемінде бір белсенді әкімші қалуы керек.")
                    encoded = hash_password(password) if password else previous["password_hash"]
                    conn.execute("UPDATE users SET username=?,display_name=?,role=?,password_hash=?,active=?,failed_attempts=0,locked_until=NULL WHERE id=?", (username,display_name,role,encoded,int(active),record_id))
                else:
                    record_id = conn.execute("INSERT INTO users(username,display_name,role,password_hash,active) VALUES (?,?,?,?,?)", (username,display_name,role,hash_password(password),int(active))).lastrowid
                _audit(conn, actor_id, "Қызметкерді сақтау", "users", record_id, ROLES[role])
                return record_id
        except sqlite3.IntegrityError as error:
            raise ValidationError(_integrity_message(error)) from None

    def change_password(self, actor_id, old_password, new_password):
        if not 8 <= len(new_password) <= 128:
            raise ValidationError("Жаңа құпиясөз 8–128 таңба болуы керек.")
        with connection(self.path) as conn:
            _require(conn, actor_id)
            row = conn.execute("SELECT password_hash FROM users WHERE id=?", (actor_id,)).fetchone()
            if not verify_password(old_password, row["password_hash"]):
                raise ValidationError("Қазіргі құпиясөз дұрыс емес.")
            conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password),actor_id))
            _audit(conn, actor_id, "Құпиясөзді өзгерту", "users", actor_id)

    def audit(self, actor_id):
        with connection(self.path) as conn:
            _require(conn, actor_id, admin=True)
            return [dict(r) for r in conn.execute("SELECT a.id,a.created_at,u.display_name,a.action,a.entity,a.record_id,a.details FROM audit_log a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT 300")]

    def backup(self, actor_id):
        with connection(self.path) as conn:
            _require(conn, actor_id, admin=True)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "clinic-backup.db"
            with connection(self.path) as src:
                dest = sqlite3.connect(path)
                try:
                    src.backup(dest)
                finally:
                    dest.close()
            return path.read_bytes()
