import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from .main import app, get_db
from .database import Base
from . import models


client = TestClient(app)
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "loan_app"


def test_create_user():
    email: string = "rmiller@email.com"
    response = client.post("/users/", json={"email": email})
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["id"] == 3


def test_create_user__duplicate_user():
    email: string = "jsmith@email.com"
    response = client.post("/users/", json={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_create_user__missing_email():
    with pytest.raises(NameError):
        response = client.post("/users/", json={"text": email})


def test_read_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["email"] == "jsmith@email.com"
    assert response.json()[0]["id"] == 1 
    assert response.json()[1]["email"] == "jdoe@email.com"
    assert response.json()[1]["id"] == 2 


def test_read_user():
    response = client.get("/users/2")
    assert response.status_code == 200
    assert response.json()["email"] == "jdoe@email.com"
    assert response.json()["id"] == 2 


def test_read_user__user_does_not_exist():
    response = client.get("/users/3")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_loan_for_user():
    response = client.post("/users/loans/", json={"user_ids": [1, 2], "amount": 3000000, "rate": 375, "term": 12})
    assert response.status_code == 200
    assert response.json()["amount"] == 3000000
    assert response.json()["rate"] == 375
    assert response.json()["term"] == 12 
    assert response.json()["id"] == 4
    assert len(response.json()["users"]) == 2
    assert response.json()["users"][0]["id"] == 1
    assert response.json()["users"][0]["email"] == "jsmith@email.com"
    assert response.json()["users"][1]["id"] == 2
    assert response.json()["users"][1]["email"] == "jdoe@email.com"


def test_create_loan_for_user__user_does_not_exist():
    response = client.post("/users/loans/", json={"user_ids": [1, 2, 3], "amount": 3000000, "rate": 375, "term": 12})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_loan_for_user__missing_amount():
    response = client.post("/users/loans/", json={"user_ids": [1, 2], "text": 3000000, "rate": 375, "term": 12})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.json()["detail"][0]["loc"] == ["body", "amount"]


def test_read_loans():
    response = client.get("/loans/")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_read_loan():
    response = client.get("/loans/3")
    assert response.status_code == 200
    assert response.json()["amount"] == 60000000
    assert response.json()["rate"] == 800
    assert response.json()["term"] == 360
    assert response.json()["id"] == 3
    assert len(response.json()["users"]) == 2
    assert response.json()["users"][0]["id"] == 1
    assert response.json()["users"][0]["email"] == "jsmith@email.com"
    assert response.json()["users"][1]["id"] == 2
    assert response.json()["users"][1]["email"] == "jdoe@email.com"


def test_read_loan__loan_does_not_exist():
    response = client.get("/loans/4")
    assert response.status_code == 404
    assert response.json()["detail"] == "Loan not found"


def test_read_loan_schedule():
    response = client.get("/loans/1/schedule")
    assert response.status_code == 200
    assert len(response.json()) == 24
    assert response.json()[0]["month"] == 1
    assert response.json()[0]["interest_payment"] == 33333
    assert response.json()[0]["principal_payment"] == 400916
    assert response.json()[0]["monthly_payment"] == 434249
    assert response.json()[0]["remaining_balance"] == 9599084
    assert response.json()[23]["month"] == 24
    assert response.json()[23]["interest_payment"] == 1443
    assert response.json()[23]["principal_payment"] == 432814
    assert response.json()[23]["monthly_payment"] == 434257
    assert response.json()[23]["remaining_balance"] == 0


def test_read_loan_schedule__loan_does_not_exist():
    response = client.get("/loans/4/schedule")
    assert response.status_code == 404
    assert response.json()["detail"] == "Loan not found"


def test_read_loans_for_user():
    response = client.get("/users/2/loans")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_loans_for_user__user_does_not_exist():
    response = client.get("/users/3/loans")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_read_loan_summary():
    response = client.get("/loans/1/summary?month=20")
    assert response.status_code == 200
    assert response.json()["loan_id"] == 1
    assert response.json()["month"] == 20
    assert response.json()["principal_balance"] == 1294117
    assert response.json()["aggregate_principal_paid"] == 8304967
    assert response.json()["aggregate_interest_paid"] == 380013


def test_read_loan_summary__loan_does_not_exist():
    response = client.get("/loans/4/summary?month=2")
    assert response.status_code == 404
    assert response.json()["detail"] == "Loan not found"


def test_read_loan_summary__month_higher_than_loan_term():
    response = client.get("/loans/1/summary?month=25")
    assert response.status_code == 400
    assert response.json()["detail"] == "Month higher than loan term"


def setup() -> None:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    emails = ["jsmith@email.com", "jdoe@email.com"]
    for curr_email in emails:
        db_user = models.User(email=curr_email)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    session.close()

    session = TestingSessionLocal()
    loans_details = [
        {
            "users": [1],
            "amount": 10000000,
            "rate": 400,
            "term": 24
        },
        {
            "users": [2],
            "amount": 20000000,
            "rate": 450,
            "term": 48 
        },
        {
            "users": [1, 2],
            "amount": 60000000,
            "rate": 800,
            "term": 360
        }

    ]
    for i in range(len(loans_details)):
        loan_details = loans_details[i]
        db_users = session.query(models.User).filter(models.User.id.in_(loan_details["users"])).all()
        db_loan = models.Loan(
            amount=loan_details["amount"],
            rate=loan_details["rate"],
            term=loan_details["term"],
            users=db_users
        )
        session.add(db_loan)
        session.commit()
        session.refresh(db_loan)

    session.close()


def teardown() -> None:
    Base.metadata.drop_all(bind=engine)
