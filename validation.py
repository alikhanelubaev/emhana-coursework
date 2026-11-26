"""Форма мен қызмет қабатына ортақ валидация."""
from datetime import date, datetime
import re
from errors import ValidationError
from models import ENTITIES, LABELS


def text(value, label: str, minimum: int = 2, maximum: int = 2000) -> str:
    result = str(value or "").strip()
    if not minimum <= len(result) <= maximum:
        raise ValidationError(f"«{label}» ұзындығы {minimum}–{maximum} таңба болуы керек.")
    return result


def phone(value) -> str:
    raw = str(value or "").strip()
    if re.search(r"[^\d+()\s-]", raw):
        raise ValidationError("Телефонда тек сандар, +, жақша және сызықша болсын.")
    digits = re.sub(r"\D", "", raw)
    if not 10 <= len(digits) <= 15:
        raise ValidationError("Телефон нөмірінде 10–15 сан болуы керек.")
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return "+" + digits


def iso_date(value, label: str) -> str:
    try:
        return date.fromisoformat(str(value)).isoformat()
    except (ValueError, TypeError):
        raise ValidationError(f"«{label}» дұрыс күн болуы керек: ЖЖЖЖ-АА-КК.") from None


def positive_id(value, label="Нөмір") -> int:
    try:
        result = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"«{label}» оң бүтін сан болуы керек.") from None
    if isinstance(value, bool) or str(result) != str(value).strip() or result < 1:
        raise ValidationError(f"«{label}» оң бүтін сан болуы керек.")
    return result


def entity_data(entity: str, values: dict) -> dict:
    if entity not in ENTITIES:
        raise ValidationError("Белгісіз кесте.")
    result = {}
    for key in ENTITIES[entity].fields:
        value = values.get(key)
        if key in {"patient_id", "doctor_id", "cabinet"}:
            result[key] = positive_id(value, LABELS[key])
        elif key == "phone":
            result[key] = phone(value)
        elif key in {"birth_date", "appointment_date", "record_date"}:
            result[key] = iso_date(value, LABELS[key])
        elif key == "gender":
            if value not in {"Ер", "Әйел"}:
                raise ValidationError("Жынысын «Ер» немесе «Әйел» деп таңдаңыз.")
            result[key] = value
        elif key == "appointment_time":
            try:
                result[key] = datetime.strptime(str(value), "%H:%M").strftime("%H:%M")
            except (ValueError, TypeError):
                raise ValidationError("Уақытты СС:ММ пішімінде енгізіңіз.") from None
        else:
            maximum = 150 if key in {"full_name", "specialization", "diagnosis"} else 2000
            result[key] = text(value, LABELS[key], maximum=maximum)
    if entity == "patients" and result["birth_date"] > date.today().isoformat():
        raise ValidationError("Туған күн бүгіннен кейін болмауы керек.")
    if entity == "medical_records" and result["record_date"] > date.today().isoformat():
        raise ValidationError("Медициналық жазба күні бүгіннен кейін болмауы керек.")
    if entity == "doctors" and result["cabinet"] > 9999:
        raise ValidationError("Кабинет нөмірі 1–9999 аралығында болсын.")
    return result
