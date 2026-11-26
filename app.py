"""Emhana: барлық интерфейс Streamlit виджеттерімен Python ішінде жасалған."""
from datetime import date, datetime, time
import logging
import sqlite3
import time as clock
import pandas as pd
import streamlit as st
from database import database_path, initialize_database
from errors import AppError
from models import ENTITIES, LABELS, ROLES
from queries import QUERIES, run_query
from services import ClinicService, can_write

st.set_page_config(page_title="Emhana · Емхана картотекасы", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")
LOG = logging.getLogger("emhana")
PAGES = ["Басты бет", "Пациенттер", "Дәрігерлер", "Қабылдаулар", "Медициналық жазбалар", "Пациент картасы", "Есептер", "SQL сұраныстары", "Баптаулар"]


@st.cache_resource
def bootstrap(path):
    initialize_database(path)
    return path


def notify(message):
    st.session_state["flash_message"] = message
    st.rerun()


def route(page):
    st.session_state["pending_page"] = page
    st.rerun()


def dataframe(rows, key=None):
    if not rows:
        st.info("Мәлімет табылмады. Іздеу немесе сүзгі шарттарын өзгертіңіз.")
        return
    frame = pd.DataFrame(rows).rename(columns=LABELS)
    st.dataframe(frame, hide_index=True, width="stretch", key=key)
    st.caption(f"Жазбалар саны: {len(frame)}")


def csv_download(rows, filename):
    if rows:
        frame = pd.DataFrame(rows).rename(columns=LABELS)
        # Prevent spreadsheet formula execution when a text cell starts with = + - @.
        for column in frame.columns:
            frame[column] = frame[column].map(lambda v: "'"+v if isinstance(v,str) and v.startswith(("=","+","-","@")) else v)
        st.download_button("CSV жүктеу", frame.to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key="csv_"+filename)


def login(service):
    left, right = st.columns([1.15,1], gap="large")
    with left:
        st.title("🏥 Emhana")
        st.header("Әр пациенттің тарихы — бір жүйеде")
        st.write("Қалалық емхана пациенттерінің картотекасы. Пациенттерді тіркеңіз, қабылдауға жазыңыз және медициналық тарихын жүргізіңіз.")
        st.divider()
        st.write("**Пациенттер → Қабылдаулар → Медициналық жазбалар**")
        st.caption("Python · SQLite · Streamlit. Жергілікті қосымша, мәліметтер осы ноутбукте сақталады.")
    with right:
        with st.container(border=True):
            st.subheader("Жүйеге кіру")
            with st.form("login_form"):
                username = st.text_input("Логин", key="login_username", max_chars=40)
                password = st.text_input("Құпиясөз", type="password", key="login_password", max_chars=128)
                submitted = st.form_submit_button("Жүйеге кіру", type="primary", width="stretch")
            if submitted:
                try:
                    user = service.authenticate(username, password)
                    st.session_state["auth_id"] = user["id"]
                    st.session_state["auth_started"] = clock.time()
                    st.session_state["navigation"] = "Басты бет"
                    st.rerun()
                except AppError as error:
                    st.error(str(error))
            st.caption("Алғашқы кіру: admin / Clinic2026. Баптаулар бөлімінде құпиясөзді өзгертуге болады.")
    st.info("Бастапқы пациенттер мен медициналық жазбалар — курстықтағы тестілік деректер.")


def home(service):
    st.title("Картотекаға шолу")
    st.write("Пациенттер, дәрігерлер және қабылдаулар туралы бірыңғай ақпарат.")
    counts = service.counts()
    for col, (entity, count) in zip(st.columns(4), counts.items()):
        col.metric(ENTITIES[entity].title, count)
    st.divider()
    left, right = st.columns([1.6,1], gap="large")
    with left:
        st.subheader("Соңғы қабылдаулар")
        rows = service.list_records("appointments",sort="appointment_date",descending=True)[:5]
        dataframe([{k:r[k] for k in ("appointment_date","appointment_time","patient_name","doctor_name","reason")} for r in rows])
    with right:
        with st.container(border=True):
            st.subheader("Жылдам өту")
            for label, page in [("Пациенттерді ашу","Пациенттер"),("Қабылдауларды ашу","Қабылдаулар"),("Пациент картасын ашу","Пациент картасы")]:
                if st.button(label, width="stretch"):
                    route(page)
            today_count = service.read("SELECT COUNT(*) count FROM appointments WHERE appointment_date=?", (date.today().isoformat(),))[0]["count"]
            st.metric("Бүгінгі қабылдау", today_count)
    st.caption("Әр өзгеріс SQLite базасына бірден сақталады. Бетті жаңарту немесе қосымшаны қайта қосу деректерді өшірмейді.")


def choose_record(service, entity, label="Жазбаны таңдаңыз"):
    rows = service.list_records(entity)
    if not rows:
        st.info("Алдымен жаңа жазба қосыңыз.")
        return None
    lookup = {r["id"]:r for r in rows}
    def display(record_id):
        row = lookup[record_id]
        detail = row.get("full_name") or row.get("patient_name")
        suffix = row.get("appointment_date", row.get("record_date", ""))
        return f"№ {record_id} · {detail} · {suffix}".rstrip(" ·")
    record_id = st.selectbox(label,list(lookup),format_func=display,key=entity+"_selected")
    return service.get(entity,record_id)


def list_page(service, entity):
    search = st.text_input("Іздеу",placeholder="Аты-жөні, телефон немесе басқа мәлімет",key=entity+"_search")
    filters = {}
    a,b,c = st.columns(3)
    with a:
        if entity == "patients":
            gender = st.selectbox("Жынысы",["Барлығы","Ер","Әйел"])
            if gender != "Барлығы": filters["gender"] = gender
        elif entity == "doctors":
            options = [r["specialization"] for r in service.read("SELECT DISTINCT specialization FROM doctors ORDER BY specialization")]
            value = st.selectbox("Мамандығы",["Барлығы"]+options)
            if value != "Барлығы": filters["specialization"] = value
        elif entity == "appointments":
            doctors = {r["id"]:r["full_name"] for r in service.list_records("doctors",sort="full_name")}
            value = st.selectbox("Дәрігер",[None]+list(doctors),format_func=lambda i:"Барлығы" if i is None else doctors[i])
            if value is not None: filters["doctor_id"] = value
        else:
            options = [r["diagnosis"] for r in service.read("SELECT DISTINCT diagnosis FROM medical_records ORDER BY diagnosis")]
            value = st.selectbox("Диагноз",["Барлығы"]+options)
            if value != "Барлығы": filters["diagnosis"] = value
    with b:
        sort = st.selectbox("Сұрыптау өрісі",ENTITIES[entity].sort_fields,format_func=lambda f:LABELS[f],key=entity+"_sort")
    with c:
        order = st.selectbox("Сұрыптау бағыты",["Өсу ретімен","Кему ретімен"],key=entity+"_order")
    if entity in {"appointments","medical_records"} and st.checkbox("Күн аралығы бойынша сүзу",key=entity+"_date_filter"):
        left,right = st.columns(2)
        filters["start_date"] = left.date_input("Басталу күні",date(2026,9,1),key=entity+"_start").isoformat()
        filters["end_date"] = right.date_input("Аяқталу күні",date.today(),key=entity+"_end").isoformat()
    try:
        rows = service.list_records(entity,search,filters,sort,order=="Кему ретімен")
        dataframe(rows)
        csv_download(rows,entity+".csv")
    except AppError as error:
        st.error(str(error))


def entity_form(service, entity, actor, record=None):
    patients = {r["id"]:r["full_name"] for r in service.list_records("patients",sort="full_name")}
    doctors = {r["id"]:r["full_name"]+" · "+r["specialization"] for r in service.list_records("doctors",sort="full_name")}
    if entity in {"appointments","medical_records"} and not patients:
        st.warning("Алдымен пациентті тіркеңіз.")
        return
    if entity == "appointments" and not doctors:
        st.warning("Алдымен дәрігерді тіркеңіз.")
        return
    generation = st.session_state.get(entity+"_generation",0)
    form_key = f"form_{entity}_{record['id'] if record else 'new'}_{generation}"
    values = record or {}
    with st.form(form_key):
        data = {}
        for field in ENTITIES[entity].fields:
            label = LABELS[field]
            widget_key = form_key+"_"+field
            if field in {"patient_id","doctor_id"}:
                options = patients if field=="patient_id" else doctors
                ids = list(options)
                index = ids.index(values[field]) if values.get(field) in ids else 0
                data[field] = st.selectbox("Пациент" if field=="patient_id" else "Дәрігер",ids,index=index,format_func=lambda i,lookup=options:lookup[i],key=widget_key)
            elif field in {"birth_date","appointment_date","record_date"}:
                default = date.fromisoformat(values[field]) if values.get(field) else (date(2000,1,1) if field=="birth_date" else date.today())
                maximum = date.today() if field in {"birth_date","record_date"} else date(2100,12,31)
                data[field] = st.date_input(label,default,min_value=date(1900,1,1),max_value=maximum,key=widget_key).isoformat()
            elif field == "appointment_time":
                default = datetime.strptime(values[field],"%H:%M").time() if values.get(field) else time(9,0)
                data[field] = st.time_input(label,default,step=300,key=widget_key).strftime("%H:%M")
            elif field == "gender":
                data[field] = st.selectbox(label,["Ер","Әйел"],index=1 if values.get(field)=="Әйел" else 0,key=widget_key)
            elif field == "cabinet":
                data[field] = st.number_input(label,min_value=1,max_value=9999,value=int(values.get(field,101)),step=1,key=widget_key)
            elif field in {"address","reason","complaint","recommendation"}:
                data[field] = st.text_area(label,value=values.get(field,""),max_chars=2000,key=widget_key,height=90)
            else:
                data[field] = st.text_input(label,value=values.get(field,""),max_chars=150,key=widget_key)
        submitted = st.form_submit_button("Өзгерістерді сақтау" if record else "Жазбаны қосу",type="primary")
    if submitted:
        try:
            record_id = service.save(entity,data,actor["id"],record["id"] if record else None)
            st.session_state[entity+"_generation"] = generation+1
            notify(f"№ {record_id} жазба сәтті сақталды.")
        except AppError as error:
            st.error(str(error))


def entity_page(service, entity, user):
    st.title(ENTITIES[entity].title)
    st.caption("Деректер SQLite базасынан оқылады және сол базаға сақталады.")
    options = ["Тізім","Қосу","Өзгерту","Жою"] if can_write(user,entity) else ["Тізім"]
    mode = st.radio("Әрекет",options,horizontal=True,key=entity+"_mode")
    if mode == "Тізім":
        list_page(service,entity)
    elif mode == "Қосу":
        st.subheader("Жаңа жазба")
        entity_form(service,entity,user)
    elif mode == "Өзгерту":
        record = choose_record(service,entity)
        if record:
            entity_form(service,entity,user,record)
    else:
        record = choose_record(service,entity)
        if record:
            dataframe([record])
            st.warning("Жою әрекеті таңдалған жазбаға ғана қолданылады. Байланысты жазбалар болса, база оны жоюға жол бермейді.")
            confirm = st.checkbox(f"№ {record['id']} жазбаны жоюды растаймын",key=f"confirm_{entity}_{record['id']}")
            if st.button("Жазбаны жою",disabled=not confirm,type="primary"):
                try:
                    service.delete(entity,record["id"],user["id"])
                    notify("Жазба сәтті жойылды.")
                except AppError as error:
                    st.error(str(error))


def patient_card(service):
    st.title("Пациенттің толық картасы")
    patients = {r["id"]:r["full_name"] for r in service.list_records("patients",sort="full_name")}
    if not patients:
        st.info("Пациенттер әлі тіркелмеген.")
        return
    selected = st.selectbox("Пациентті таңдаңыз",list(patients),format_func=lambda i:f"№ {i} · {patients[i]}",key="card_patient")
    card = service.patient_card(selected)
    with st.container(border=True):
        st.subheader(card["patient"]["full_name"])
        a,b,c = st.columns(3)
        born = date.fromisoformat(card["patient"]["birth_date"])
        today = date.today()
        a.metric("Жасы",today.year-born.year-((today.month,today.day)<(born.month,born.day)))
        b.metric("Қабылдаулар",len(card["appointments"]))
        c.metric("Медициналық жазбалар",len(card["records"]))
        dataframe([card["patient"]])
    first, second = st.tabs(["Қабылдау тарихы","Медициналық жазбалар"])
    with first:
        dataframe(card["appointments"])
    with second:
        if not card["records"]:
            st.info("Медициналық жазба жоқ.")
        for row in card["records"]:
            with st.expander(f"{row['record_date']} · {row['diagnosis']}",expanded=True):
                st.write("**Шағымы:**",row["complaint"])
                st.write("**Ұсынысы:**",row["recommendation"])


def reports(service):
    st.title("Есептер мен статистика")
    kind = st.radio("Есеп түрі",["Дәрігер жүктемесі","Диагноздар","Жынысы бойынша","Қайта келгендер","Күндер бойынша"],horizontal=True)
    if kind == "Дәрігер жүктемесі":
        rows = run_query(service,"doctor_workload")
        dataframe(rows)
        if rows: st.bar_chart(pd.DataFrame(rows).set_index("doctor_name")[["count"]])
    elif kind == "Диагноздар":
        minimum = st.number_input("Диагноз бойынша ең аз жазба саны",min_value=1,max_value=100000,value=1,step=1)
        rows = run_query(service,"records_by_diagnosis",minimum_count=minimum)
        dataframe(rows)
        if rows: st.bar_chart(pd.DataFrame(rows).set_index("diagnosis")[["count"]])
    elif kind == "Жынысы бойынша":
        rows = run_query(service,"patients_by_gender")
        dataframe(rows)
        if rows: st.bar_chart(pd.DataFrame(rows).set_index("gender")[["count"]])
    elif kind == "Қайта келгендер":
        rows = run_query(service,"frequent_patients")
        dataframe(rows)
    else:
        rows = service.read("SELECT appointment_date,COUNT(*) count FROM appointments GROUP BY appointment_date ORDER BY appointment_date")
        dataframe(rows)
        if rows:
            frame = pd.DataFrame(rows)
            frame["appointment_date"] = pd.to_datetime(frame["appointment_date"])
            st.line_chart(frame.set_index("appointment_date")[["count"]])
    csv_download(rows,"report.csv")


def sql_queries(service):
    st.title("SQL сұраныстары")
    st.write("Курстықтың 3.4–3.6 бөлімдеріндегі сұраныстарды нақты SQLite базасында орындау.")
    key = st.selectbox("Сұраныс",list(QUERIES),format_func=lambda k:QUERIES[k].title)
    query = QUERIES[key]
    st.caption("Курстықтағы бөлім: "+query.section)
    st.code(query.sql,language="sql")
    values = {}
    with st.form("query_"+key):
        for param in query.parameters:
            if param in {"reference_date","start_date","end_date"}:
                default = date(2026,10,1) if param=="reference_date" else (date(2026,9,10) if param=="start_date" else date(2026,9,12))
                values[param] = st.date_input({"reference_date":"Жасты есептеу күні","start_date":"Басталу күні","end_date":"Аяқталу күні"}[param],default).isoformat()
            elif param == "before_date":
                year = st.number_input("Осы жылға дейін туған",min_value=1901,max_value=date.today().year,value=2000,step=1)
                values[param] = f"{year}-01-01"
            elif param == "minimum_count":
                values[param] = st.number_input("Ең аз жазба саны",min_value=1,value=3,step=1)
            elif param == "prefix":
                values[param] = st.text_input("Аты-жөнінің басы",value="А")
            elif param == "specialization":
                options = [r["specialization"] for r in service.read("SELECT DISTINCT specialization FROM doctors ORDER BY specialization")]
                values[param] = st.selectbox("Мамандығы",options) if options else ""
            elif param == "diagnosis":
                options = [r["diagnosis"] for r in service.read("SELECT DISTINCT diagnosis FROM medical_records ORDER BY diagnosis")]
                values[param] = st.selectbox("Диагноз",options) if options else ""
        submitted = st.form_submit_button("Сұранысты орындау",type="primary")
    if submitted:
        try:
            rows = run_query(service,key,**values)
            dataframe(rows)
            csv_download(rows,"query.csv")
        except AppError as error:
            st.error(str(error))
    st.caption("LIKE іздеуінде қазақша әріптердің регистрі casefold арқылы өңделеді. Еркін SQL енгізілмейді: сұраныстар бекітілген тізімнен орындалады.")


def user_management(service, user):
    rows = service.list_users(user["id"])
    shown = [{**r,"role":ROLES[r["role"]],"active":"Иә" if r["active"] else "Жоқ"} for r in rows]
    dataframe(shown)
    mode = st.radio("Қызметкер әрекеті",["Қосу","Өзгерту"],horizontal=True)
    record = None
    if mode == "Өзгерту":
        lookup = {r["id"]:r for r in rows}
        selected = st.selectbox("Қызметкер",list(lookup),format_func=lambda i:lookup[i]["username"])
        record = lookup[selected]
    current = record or {}
    with st.form(f"user_form_{current.get('id','new')}"):
        username = st.text_input("Қызметкер логині",value=current.get("username",""))
        name = st.text_input("Қызметкер аты-жөні",value=current.get("display_name",""))
        role = st.selectbox("Рөлі",list(ROLES),index=list(ROLES).index(current.get("role","registrar")),format_func=lambda r:ROLES[r])
        password = st.text_input("Жаңа құпиясөз"+(" (өзгермесе бос қалдырыңыз)" if record else ""),type="password")
        active = st.checkbox("Белсенді қызметкер",value=bool(current.get("active",True)))
        submitted = st.form_submit_button("Қызметкерді сақтау",type="primary")
    if submitted:
        try:
            service.save_user(user["id"],username,name,role,password,active,current.get("id"))
            notify("Қызметкер сақталды.")
        except AppError as error:
            st.error(str(error))
    st.caption("Тіркеуші пациенттер мен қабылдауларды өзгертеді. Дәрігер медициналық жазбаларды өзгертеді. Әкімші барлық бөлімді басқарады.")


def settings(service, user):
    st.title("Баптаулар")
    tabs = st.tabs(["Менің аккаунтым","Қызметкерлер","Әрекеттер журналы","Деректер базасы"] if user["role"]=="admin" else ["Менің аккаунтым"])
    with tabs[0]:
        st.write(f"**{user['display_name']}** · {ROLES[user['role']]}")
        with st.form("change_password"):
            old = st.text_input("Қазіргі құпиясөз",type="password")
            new = st.text_input("Жаңа құпиясөз",type="password")
            confirm = st.text_input("Жаңа құпиясөзді қайталаңыз",type="password")
            submitted = st.form_submit_button("Құпиясөзді өзгерту")
        if submitted:
            try:
                if new != confirm:
                    st.error("Жаңа құпиясөздер сәйкес емес.")
                else:
                    service.change_password(user["id"],old,new)
                    notify("Құпиясөз өзгертілді.")
            except AppError as error:
                st.error(str(error))
    if user["role"] == "admin":
        with tabs[1]: user_management(service,user)
        with tabs[2]:
            st.caption("Соңғы 300 әрекет. Уақыт UTC пішімінде сақталады.")
            dataframe(service.audit(user["id"]))
        with tabs[3]:
            st.write("**SQLite файлы:**",str(service.path))
            st.write("**Тұтастық тексеруі:**",service.read("PRAGMA integrity_check")[0]["integrity_check"])
            st.download_button("Базаның сақтық көшірмесін жүктеу",service.backup(user["id"]),f"clinic-backup-{date.today()}.db",mime="application/octet-stream")
            for row in service.read("SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
                with st.expander(row["name"]):st.code(row["sql"],language="sql")


def main():
    path = database_path()
    try:
        bootstrap(str(path))
        service = ClinicService(path)
        user = service.user(st.session_state.get("auth_id"))
        if user and clock.time()-st.session_state.get("auth_started",0)>8*3600:
            st.session_state.pop("auth_id",None)
            user = None
        if not user:
            login(service)
            return
        if "pending_page" in st.session_state:
            st.session_state["navigation"] = st.session_state.pop("pending_page")
        with st.sidebar:
            st.title("🏥 Emhana")
            st.caption("Қалалық емхана картотекасы")
            st.write("**"+user["display_name"]+"**")
            st.caption(ROLES[user["role"]])
            page = st.radio("Бөлім",PAGES,key="navigation")
            st.divider()
            if st.button("Жүйеден шығу",width="stretch"):
                st.session_state.clear()
                st.rerun()
            st.caption("Python + SQLite + Streamlit")
        if "flash_message" in st.session_state:
            st.success(st.session_state.pop("flash_message"))
        entities_by_page = {spec.title:key for key,spec in ENTITIES.items()}
        if page in entities_by_page: entity_page(service,entities_by_page[page],user)
        elif page == "Басты бет": home(service)
        elif page == "Пациент картасы": patient_card(service)
        elif page == "Есептер": reports(service)
        elif page == "SQL сұраныстары": sql_queries(service)
        else: settings(service,user)
    except AppError as error:
        st.error(str(error))
    except sqlite3.Error:
        LOG.exception("SQLite operation failed")
        st.error("Деректер базасына қол жеткізу мүмкін болмады. Қапшықтың жазу құқығын тексеріп, әрекетті қайталаңыз.")


if __name__ == "__main__":
    main()
