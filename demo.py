"""Курстықтағы INSERT/UPDATE/DELETE және SQL мысалдары: оқшауланған уақытша база."""
from pathlib import Path
import sys
import tempfile
from database import connection,initialize_database
from seed import PATIENTS,DOCTORS,APPOINTMENTS,MEDICAL_RECORDS
from services import ClinicService
from models import ENTITIES
from queries import QUERIES,run_query


def show(title,rows):
    print("\n"+title)
    for row in rows:print(" | ".join(f"{key}: {value}" for key,value in row.items()))
    print(f"Жол саны: {len(rows)}")


def main():
    if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="emhana-sql-demo-") as folder:
        path=Path(folder)/"demo.db"
        initialize_database(path,seed=False)
        service=ClinicService(path)
        print("Уақытша оқу базасы. Негізгі clinic.db өзгертілмейді.")
        initial_patients=[list(r) for r in PATIENTS[:5]]
        initial_patients[4][5]="Астана"
        initial_appointments=[list(r) for r in APPOINTMENTS[:5]]
        initial_appointments[4][3:5]=["2026-09-12","14:00"]
        sources={"patients":initial_patients,"doctors":DOCTORS[:5],"appointments":initial_appointments,"medical_records":MEDICAL_RECORDS[:5]}
        for entity,rows in sources.items():
            for row in rows:service.save(entity,dict(zip(ENTITIES[entity].fields,row[1:])),1)
        print("Бастапқы деректер:",service.counts())
        sources={"patients":PATIENTS[5:],"doctors":DOCTORS[5:],"appointments":APPOINTMENTS[5:],"medical_records":MEDICAL_RECORDS[5:]}
        for entity,rows in sources.items():
            for row in rows:service.save(entity,dict(zip(ENTITIES[entity].fields,row[1:])),1)
        print("INSERT нәтижесі:",service.counts())
        patient=service.get("patients",5);patient["address"]="Астана, Сарыарқа ауданы"
        service.save("patients",patient,1,5)
        appointment=service.get("appointments",5)
        appointment.update(appointment_date="2026-09-13",appointment_time="15:30")
        service.save("appointments",appointment,1,5)
        print("UPDATE:",service.get("patients",5)["address"],service.get("appointments",5)["appointment_date"])
        wrong=service.save("appointments",{"patient_id":5,"doctor_id":5,"appointment_date":"2026-09-25","appointment_time":"10:00","reason":"Қате жазба"},1)
        before=service.counts()["appointments"]
        service.delete("appointments",wrong,1)
        print("DELETE:",before,"→",service.counts()["appointments"])
        values={"reference_date":"2026-10-01","specialization":"Терапевт","prefix":"А","start_date":"2026-09-10","end_date":"2026-09-12","before_date":"2000-01-01","minimum_count":3,"diagnosis":"Гипертония"}
        for key,query in QUERIES.items():
            show(query.title,run_query(service,key,**{p:values[p] for p in query.parameters}))
        card=service.patient_card(1)
        show("Пациент картасы: жеке мәліметтер",[card["patient"]])
        show("Пациент картасы: қабылдаулар",card["appointments"])
        show("Пациент картасы: медициналық жазбалар",card["records"])
        print("Тұтастық:",service.read("PRAGMA integrity_check")[0]["integrity_check"])


if __name__=="__main__":
    main()
