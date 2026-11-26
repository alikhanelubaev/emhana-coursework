from datetime import date,timedelta
import sqlite3
import pytest
from database import connection,initialize_database
from errors import AccessError,LoginError,NotFoundError,ValidationError
from queries import QUERIES,run_query
from security import hash_password,verify_password


def test_initial_counts_and_idempotent_start(service,patient_values):
    assert service.counts()=={"patients":8,"doctors":6,"appointments":12,"medical_records":10}
    new_id=service.save("patients",patient_values,1)
    initialize_database(service.path)
    assert service.get("patients",new_id)["full_name"]==patient_values["full_name"]
    assert service.counts()["patients"]==9


def test_patient_crud_and_restart(service,patient_values):
    new_id=service.save("patients",patient_values,1)
    patient_values["address"]="Астана, жаңа мекенжай"
    service.save("patients",patient_values,1,new_id)
    initialize_database(service.path)
    assert service.get("patients",new_id)["address"]==patient_values["address"]
    service.delete("patients",new_id,1)
    with pytest.raises(NotFoundError):service.get("patients",new_id)
    initialize_database(service.path)
    assert service.counts()["patients"]==8


def test_doctor_crud(service):
    values={"full_name":"Тест Дәрігер","specialization":"Терапевт","phone":"87001002031","cabinet":201}
    new_id=service.save("doctors",values,1)
    values["cabinet"]=202
    service.save("doctors",values,1,new_id)
    assert service.get("doctors",new_id)["cabinet"]==202
    service.delete("doctors",new_id,1)
    assert service.counts()["doctors"]==6


def test_appointment_crud_and_join(service):
    values={"patient_id":1,"doctor_id":1,"appointment_date":"2027-01-03","appointment_time":"10:00","reason":"Тест қабылдау"}
    new_id=service.save("appointments",values,1)
    values["appointment_time"]="11:00"
    service.save("appointments",values,1,new_id)
    row=next(r for r in service.list_records("appointments") if r["id"]==new_id)
    assert row["appointment_time"]=="11:00" and row["patient_name"]=="Айдос Нұрланов"
    service.delete("appointments",new_id,1)
    assert service.counts()["appointments"]==12


def test_medical_record_crud(service):
    values={"patient_id":1,"record_date":"2026-10-01","diagnosis":"Тест диагноз","complaint":"Тест шағым","recommendation":"Тест ұсыныс"}
    new_id=service.save("medical_records",values,1)
    values["recommendation"]="Жаңартылған ұсыныс"
    service.save("medical_records",values,1,new_id)
    assert service.get("medical_records",new_id)["recommendation"]==values["recommendation"]
    service.delete("medical_records",new_id,1)
    assert service.counts()["medical_records"]==10


@pytest.mark.parametrize("field,value",[("full_name"," "),("phone","abc"),("gender","Белгісіз"),("birth_date","2026-02-30"),("birth_date",(date.today()+timedelta(days=1)).isoformat())])
def test_invalid_patient_is_not_saved(service,patient_values,field,value):
    patient_values[field]=value
    with pytest.raises(ValidationError):service.save("patients",patient_values,1)
    assert service.counts()["patients"]==8


def test_phone_normalization_prevents_duplicates(service,patient_values):
    patient_values["phone"]="+7 (700) 123-45-67"
    with pytest.raises(ValidationError,match="телефон"):service.save("patients",patient_values,1)


@pytest.mark.parametrize("entity,record_id",[("patients",1),("doctors",1)])
def test_restrict_deletion_preserves_related_records(service,entity,record_id):
    before=service.counts()
    with pytest.raises(ValidationError,match="байланысқан"):service.delete(entity,record_id,1)
    assert service.counts()==before


@pytest.mark.parametrize("field,value",[("patient_id",999),("doctor_id",999)])
def test_missing_foreign_key(service,field,value):
    values={"patient_id":1,"doctor_id":1,"appointment_date":"2027-01-01","appointment_time":"10:00","reason":"Тексеру"}
    values[field]=value
    with pytest.raises(ValidationError):service.save("appointments",values,1)
    assert service.counts()["appointments"]==12


def test_doctor_double_booking(service):
    values={"patient_id":2,"doctor_id":1,"appointment_date":"2026-09-10","appointment_time":"09:00","reason":"Қайталану"}
    with pytest.raises(ValidationError,match="Дәрігер"):service.save("appointments",values,1)


def test_patient_double_booking(service):
    values={"patient_id":1,"doctor_id":2,"appointment_date":"2026-09-10","appointment_time":"09:00","reason":"Қайталану"}
    with pytest.raises(ValidationError,match="Пациент"):service.save("appointments",values,1)


def test_dates_cannot_precede_birth(service):
    values={"patient_id":1,"doctor_id":1,"appointment_date":"2000-01-01","appointment_time":"09:00","reason":"Тексеру"}
    with pytest.raises(ValidationError,match="туған"):service.save("appointments",values,1)
    patient=service.get("patients",1)
    patient["birth_date"]="2026-10-01"
    with pytest.raises(ValidationError,match="бұрынғы"):service.save("patients",patient,1,1)


def test_search_unicode_filters_and_sort(service):
    assert service.list_records("patients",search="айдос")[0]["full_name"]=="Айдос Нұрланов"
    assert len(service.list_records("patients",filters={"gender":"Әйел"}))==4
    assert service.list_records("patients",sort="birth_date")[0]["full_name"]=="Гүлмира Тоқтарова"
    with pytest.raises(ValidationError):service.list_records("patients",sort="id;DROP TABLE patients")
    with pytest.raises(ValidationError):service.list_records("appointments",filters={"start_date":"2026-10-01","end_date":"2026-09-01"})


def test_parameterized_sql_treats_injection_as_text(service,patient_values):
    patient_values["full_name"]="Robert'); DROP TABLE patients;--"
    new_id=service.save("patients",patient_values,1)
    assert service.get("patients",new_id)["full_name"]==patient_values["full_name"]
    assert service.counts()["patients"]==9
    assert service.list_records("patients",search="' OR 1=1 --")==[]


def test_all_coursework_queries_and_expected_results(service):
    parameters={"reference_date":"2026-10-01","specialization":"Терапевт","prefix":"А","start_date":"2026-09-10","end_date":"2026-09-12","before_date":"2000-01-01","minimum_count":3,"diagnosis":"Гипертония"}
    for key,query in QUERIES.items():
        assert isinstance(run_query(service,key,**{p:parameters[p] for p in query.parameters}),list)
    assert run_query(service,"select_with_age",reference_date="2026-10-01")[0]["age"]==22
    assert len(run_query(service,"appointments_between",start_date="2026-09-10",end_date="2026-09-12"))==4
    assert len(run_query(service,"search_patients_by_name",prefix="а"))==2
    assert len(run_query(service,"records_by_diagnosis",minimum_count=3))==2
    assert len(run_query(service,"frequent_patients"))==4
    workload=run_query(service,"doctor_workload")
    assert len(workload)==6 and next(r for r in workload if r["id"]==6)["count"]==0
    assert workload[0]["count"]==4


def test_patient_card(service):
    card=service.patient_card(1)
    assert card["patient"]["full_name"]=="Айдос Нұрланов"
    assert len(card["appointments"])==2 and len(card["records"])==2


def test_password_hashes_and_login(service):
    encoded=hash_password("A-password-123")
    assert "A-password-123" not in encoded
    assert verify_password("A-password-123",encoded)
    assert not verify_password("incorrect",encoded)
    assert service.authenticate("ADMIN","Clinic2026")["role"]=="admin"
    with pytest.raises(LoginError):service.authenticate("admin","wrong")


def test_login_lockout_is_persistent(service):
    for _ in range(5):
        with pytest.raises(LoginError):service.authenticate("admin","wrong")
    with pytest.raises(LoginError,match="уақытша"):service.authenticate("admin","Clinic2026")
    initialize_database(service.path)
    with pytest.raises(LoginError,match="уақытша"):service.authenticate("admin","Clinic2026")
    with connection(service.path) as conn:conn.execute("UPDATE users SET locked_until='2000-01-01T00:00:00+00:00' WHERE id=1")
    assert service.authenticate("admin","Clinic2026")["id"]==1


def test_roles_are_enforced_in_services(service,patient_values):
    doctor=service.save_user(1,"doctor","Тест дәрігер","doctor","Doctor2026")
    registrar=service.save_user(1,"registrar","Тест тіркеуші","registrar","Register2026")
    with pytest.raises(AccessError):service.save("patients",patient_values,doctor)
    new_id=service.save("patients",patient_values,registrar)
    service.delete("patients",new_id,registrar)
    values={"patient_id":1,"record_date":"2026-10-01","diagnosis":"Тест диагноз","complaint":"Тест шағым","recommendation":"Тест ұсыныс"}
    service.save("medical_records",values,doctor)
    with pytest.raises(AccessError):service.save("medical_records",values,registrar)
    with pytest.raises(AccessError):service.list_users(doctor)
    with pytest.raises(AccessError):service.save("patients",patient_values,None)


def test_user_management_password_and_disable(service):
    uid=service.save_user(1,"registrar","Тіркеуші","registrar","Register2026")
    assert service.authenticate("registrar","Register2026")["id"]==uid
    service.change_password(uid,"Register2026","New-password-123")
    assert service.authenticate("registrar","New-password-123")["id"]==uid
    service.save_user(1,"registrar","Тіркеуші","registrar",active=False,record_id=uid)
    with pytest.raises(LoginError):service.authenticate("registrar","New-password-123")
    with pytest.raises(AccessError):service.list_users(uid)
    with pytest.raises(ValidationError):service.save_user(1,"admin","Әкімші","doctor",record_id=1)


def test_transaction_rolls_back_and_audit_is_durable(service,patient_values):
    uid=service.save("patients",patient_values,1)
    initialize_database(service.path)
    assert any(r["record_id"]==uid and r["action"]=="Қосу" for r in service.audit(1))
    before=len(service.audit(1))
    with pytest.raises(ValidationError):service.save("patients",patient_values,1)
    assert len(service.audit(1))==before


def test_backup_is_a_valid_complete_database(service,tmp_path):
    path=tmp_path/"backup.db"
    path.write_bytes(service.backup(1))
    conn=sqlite3.connect(path)
    assert conn.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    assert conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]==8
    conn.close()


def test_database_itself_enforces_constraints(service):
    with pytest.raises(sqlite3.IntegrityError):
        with connection(service.path) as conn:conn.execute("INSERT INTO patients(full_name,birth_date,gender,phone,address) VALUES (?,?,?,?,?)",("Қате","2026-02-30","Ер","+70000000000","Астана"))
    with pytest.raises(sqlite3.IntegrityError):
        with connection(service.path) as conn:conn.execute("DELETE FROM doctors WHERE id=1")
