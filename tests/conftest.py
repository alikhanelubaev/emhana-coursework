import pytest
from database import initialize_database
from services import ClinicService


@pytest.fixture
def service(tmp_path):
    path = tmp_path / "clinic.db"
    initialize_database(path)
    return ClinicService(path)


@pytest.fixture
def patient_values():
    return {"full_name":"Тест Пациент","birth_date":"2000-01-01","gender":"Ер","phone":"87001002030","address":"Астана"}
