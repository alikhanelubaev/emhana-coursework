"""Кестелердің өрістері, қазақша атаулары және рөлдер."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Entity:
    title: str
    singular: str
    fields: tuple[str, ...]
    sort_fields: tuple[str, ...]


ENTITIES = {
    "patients": Entity("Пациенттер", "Пациент", ("full_name", "birth_date", "gender", "phone", "address"), ("id", "full_name", "birth_date")),
    "doctors": Entity("Дәрігерлер", "Дәрігер", ("full_name", "specialization", "phone", "cabinet"), ("id", "full_name", "specialization", "cabinet")),
    "appointments": Entity("Қабылдаулар", "Қабылдау", ("patient_id", "doctor_id", "appointment_date", "appointment_time", "reason"), ("id", "appointment_date", "appointment_time")),
    "medical_records": Entity("Медициналық жазбалар", "Медициналық жазба", ("patient_id", "record_date", "diagnosis", "complaint", "recommendation"), ("id", "record_date", "diagnosis")),
}

LABELS = {
    "id": "№", "full_name": "Аты-жөні", "birth_date": "Туған күні", "gender": "Жынысы",
    "phone": "Телефон", "address": "Мекенжайы", "specialization": "Мамандығы", "cabinet": "Кабинет",
    "patient_id": "Пациент №", "doctor_id": "Дәрігер №", "patient_name": "Пациент", "doctor_name": "Дәрігер",
    "appointment_date": "Қабылдау күні", "appointment_time": "Уақыты", "reason": "Келу себебі",
    "record_date": "Жазба күні", "diagnosis": "Диагноз", "complaint": "Шағымы", "recommendation": "Ұсынысы",
    "age": "Жасы", "total": "Барлығы", "oldest": "Ең үлкенінің туған күні", "youngest": "Ең кішісінің туған күні",
    "count": "Саны", "visits": "Қабылдау саны", "username": "Логин", "display_name": "Қызметкер",
    "role": "Рөл", "active": "Белсенді", "created_at": "Құрылған уақыты", "action": "Әрекет",
    "entity": "Кесте", "record_id": "Жазба №", "details": "Түсіндірме",
}
ROLES = {"admin": "Әкімші", "registrar": "Тіркеуші", "doctor": "Дәрігер"}
WRITE_PERMISSIONS = {
    "admin": frozenset(ENTITIES),
    "registrar": frozenset({"patients", "appointments"}),
    "doctor": frozenset({"medical_records"}),
}
