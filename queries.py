"""Курстықтағы SQL операторлары: тек бекітілген параметрленген сұраныстар."""
from dataclasses import dataclass
from database import fold
from validation import iso_date, positive_id
from errors import ValidationError


@dataclass(frozen=True)
class Query:
    title: str
    section: str
    sql: str
    parameters: tuple[str, ...] = ()


QUERIES = {
 "select_all_patients": Query("Барлық пациенттер · SELECT *", "3.4", "SELECT * FROM patients ORDER BY id"),
 "select_columns": Query("Аты-жөні мен телефоны · SELECT", "3.4", "SELECT full_name,phone FROM patients ORDER BY full_name"),
 "select_with_age": Query("Берілген күндегі жас · есептелетін өріс", "3.4", "SELECT full_name,birth_date,CAST(strftime('%Y',:reference_date) AS INTEGER)-CAST(strftime('%Y',birth_date) AS INTEGER)-(strftime('%m-%d',:reference_date)<strftime('%m-%d',birth_date)) AS age FROM patients ORDER BY id", ("reference_date",)),
 "select_distinct_diagnoses": Query("Қайталанбайтын диагноздар · DISTINCT", "3.4", "SELECT DISTINCT diagnosis FROM medical_records ORDER BY diagnosis"),
 "select_patient_statistics": Query("Пациенттер статистикасы · COUNT MIN MAX", "3.4", "SELECT COUNT(*) total,MIN(birth_date) oldest,MAX(birth_date) youngest FROM patients"),
 "find_doctors_by_specialization": Query("Мамандығы бойынша дәрігер · WHERE", "3.5", "SELECT id,full_name,specialization,cabinet FROM doctors WHERE specialization=:specialization ORDER BY id", ("specialization",)),
 "search_patients_by_name": Query("Аты-жөнінің басы бойынша іздеу · LIKE", "3.5", "SELECT id,full_name,phone FROM patients WHERE casefold(full_name) LIKE :prefix ESCAPE '\\' ORDER BY full_name", ("prefix",)),
 "appointments_between": Query("Күн аралығындағы қабылдаулар · BETWEEN", "3.5", "SELECT id,patient_id,doctor_id,appointment_date,appointment_time,reason FROM appointments WHERE appointment_date BETWEEN :start_date AND :end_date ORDER BY appointment_date,appointment_time", ("start_date","end_date")),
 "women_born_before": Query("Берілген жылға дейін туған әйелдер · AND", "3.5", "SELECT full_name,birth_date,gender FROM patients WHERE gender='Әйел' AND birth_date<:before_date ORDER BY birth_date", ("before_date",)),
 "patients_sorted_by_birth": Query("Туған күні бойынша реттеу · ORDER BY ASC", "3.5", "SELECT full_name,birth_date FROM patients ORDER BY birth_date ASC"),
 "latest_appointments_first": Query("Соңғы бес қабылдау · DESC LIMIT", "3.5", "SELECT id,appointment_date,appointment_time,reason FROM appointments ORDER BY appointment_date DESC,appointment_time DESC LIMIT 5"),
 "patients_by_gender": Query("Жынысы бойынша пациент саны · GROUP BY", "3.5", "SELECT gender,COUNT(*) count FROM patients GROUP BY gender ORDER BY gender"),
 "records_by_diagnosis": Query("Жазбалар саны бойынша диагноздар · HAVING", "3.5", "SELECT diagnosis,COUNT(*) count FROM medical_records GROUP BY diagnosis HAVING COUNT(*)>=:minimum_count ORDER BY count DESC,diagnosis", ("minimum_count",)),
 "appointment_list": Query("Толық қабылдау тізімі · үш кесте JOIN", "3.6", "SELECT a.id,a.appointment_date,a.appointment_time,p.full_name patient_name,d.full_name doctor_name,d.specialization,a.reason FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id ORDER BY a.appointment_date,a.appointment_time"),
 "doctor_workload": Query("Дәрігерлер жүктемесі · LEFT JOIN", "3.6", "SELECT d.id,d.full_name doctor_name,d.specialization,COUNT(a.id) count FROM doctors d LEFT JOIN appointments a ON a.doctor_id=d.id GROUP BY d.id ORDER BY count DESC,d.full_name"),
 "frequent_patients": Query("Қайта келген пациенттер · JOIN GROUP BY HAVING", "3.6", "SELECT p.id,p.full_name patient_name,COUNT(a.id) visits FROM patients p JOIN appointments a ON a.patient_id=p.id GROUP BY p.id HAVING COUNT(a.id)>1 ORDER BY visits DESC,p.full_name"),
 "records_with_patients": Query("Диагноз бойынша пациенттер · JOIN WHERE", "3.6", "SELECT r.record_date,p.full_name patient_name,r.diagnosis,r.complaint,r.recommendation FROM medical_records r JOIN patients p ON p.id=r.patient_id WHERE r.diagnosis=:diagnosis ORDER BY r.record_date", ("diagnosis",)),
}


def run_query(service, key, **values):
    if key not in QUERIES:
        raise ValidationError("Сұраныс тізімнен таңдалуы керек.")
    query = QUERIES[key]
    if any(p not in values for p in query.parameters):
        raise ValidationError("Сұраныстың барлық параметрлерін толтырыңыз.")
    params = {p:values[p] for p in query.parameters}
    for name in ("reference_date","start_date","end_date","before_date"):
        if name in params:
            params[name] = iso_date(params[name], "Күн")
    if "start_date" in params and params["start_date"] > params["end_date"]:
        raise ValidationError("Басталу күні аяқталу күнінен кейін болмауы керек.")
    if "prefix" in params:
        params["prefix"] = fold(params["prefix"]).replace("\\","\\\\").replace("%","\\%").replace("_","\\_") + "%"
    if "minimum_count" in params:
        params["minimum_count"] = positive_id(params["minimum_count"], "Ең аз саны")
    return service.read(query.sql, params)
