from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from database import initialize_database
from services import ClinicService

APP=Path(__file__).resolve().parents[1]/"app.py"


@pytest.fixture
def ui(tmp_path,monkeypatch):
    path=tmp_path/"ui.db"
    monkeypatch.setenv("EMHANA_DB_PATH",str(path))
    at=AppTest.from_file(str(APP),default_timeout=20).run()
    assert not at.exception
    return at,ClinicService(path)


def login(at):
    at.text_input(key="login_username").input("admin")
    at.text_input(key="login_password").input("Clinic2026")
    next(b for b in at.button if b.label=="Жүйеге кіру").click().run()
    assert not at.exception


def test_login_and_every_navigation_page(ui):
    at,service=ui
    login(at)
    for page in ["Басты бет","Пациенттер","Дәрігерлер","Қабылдаулар","Медициналық жазбалар","Пациент картасы","Есептер","SQL сұраныстары","Баптаулар"]:
        at.sidebar.radio(key="navigation").set_value(page).run()
        assert not at.exception,(page,at.exception)
    assert service.counts()["patients"]==8


def test_form_creates_real_persistent_patient(ui):
    at,service=ui
    login(at)
    at.sidebar.radio(key="navigation").set_value("Пациенттер").run()
    at.radio(key="patients_mode").set_value("Қосу").run()
    for label,value in {"Аты-жөні":"Интерфейс Пациент","Телефон":"87001003040"}.items():
        next(w for w in at.text_input if w.label==label).input(value)
    next(w for w in at.text_area if w.label=="Мекенжайы").input("Астана")
    next(b for b in at.button if b.label=="Жазбаны қосу").click().run()
    assert not at.exception
    assert service.counts()["patients"]==9
    initialize_database(service.path)
    assert service.list_records("patients",search="Интерфейс Пациент")
    assert any("сақталды" in x.value for x in at.success)


def test_invalid_form_shows_error_without_inserting(ui):
    at,service=ui
    login(at)
    at.sidebar.radio(key="navigation").set_value("Пациенттер").run()
    at.radio(key="patients_mode").set_value("Қосу").run()
    next(b for b in at.button if b.label=="Жазбаны қосу").click().run()
    assert not at.exception
    assert at.error and service.counts()["patients"]==8


def test_sql_and_logout(ui):
    at,service=ui
    login(at)
    at.sidebar.radio(key="navigation").set_value("SQL сұраныстары").run()
    next(b for b in at.button if b.label=="Сұранысты орындау").click().run()
    assert not at.exception and len(at.dataframe[0].value)==8
    next(b for b in at.button if b.label=="Жүйеден шығу").click().run()
    assert not at.exception and at.text_input(key="login_username")


def test_edit_and_delete_through_interface(ui):
    at,service=ui
    uid=service.save("patients",{"full_name":"Өңдеу Пациент","birth_date":"2000-01-01","gender":"Ер","phone":"87001003099","address":"Бастапқы мекенжай"},1)
    login(at)
    at.sidebar.radio(key="navigation").set_value("Пациенттер").run()
    at.radio(key="patients_mode").set_value("Өзгерту").run()
    at.selectbox(key="patients_selected").set_value(uid).run()
    next(w for w in at.text_area if w.label=="Мекенжайы").input("Өзгерген мекенжай")
    next(b for b in at.button if b.label=="Өзгерістерді сақтау").click().run()
    assert not at.exception
    assert service.get("patients",uid)["address"]=="Өзгерген мекенжай"
    at.radio(key="patients_mode").set_value("Жою").run()
    at.selectbox(key="patients_selected").set_value(uid).run()
    at.checkbox(key=f"confirm_patients_{uid}").check().run()
    next(b for b in at.button if b.label=="Жазбаны жою").click().run()
    assert not at.exception and service.counts()["patients"]==8


def test_all_reports_and_parameterized_query_forms(ui):
    from queries import QUERIES
    at,service=ui
    login(at)
    at.sidebar.radio(key="navigation").set_value("Есептер").run()
    for kind in ["Дәрігер жүктемесі","Диагноздар","Жынысы бойынша","Қайта келгендер","Күндер бойынша"]:
        next(w for w in at.radio if w.label=="Есеп түрі").set_value(kind).run()
        assert not at.exception,(kind,at.exception)
        assert at.dataframe
    at.sidebar.radio(key="navigation").set_value("SQL сұраныстары").run()
    for key in QUERIES:
        next(w for w in at.selectbox if w.label=="Сұраныс").set_value(key).run()
        next(b for b in at.button if b.label=="Сұранысты орындау").click().run()
        assert not at.exception,(key,at.exception)
        assert not at.error,(key,at.error)
