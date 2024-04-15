import pytest
from .finance import *
from . import models


def test_get_pmt():
    tests = [
        {
            "principal": 0,
            "rate": 400,
            "term": 120,
            "expected_pmt": 0
        },
        {
            "principal": 50000000,
            "rate": 400,
            "term": 120,
            "expected_pmt": 506226
        },
        {
            "principal": 50000000,
            "rate": 600,
            "term": 360,
            "expected_pmt": 299775
        }
    ]
    for test in tests:
        calculated_pmt: int = get_pmt(test["principal"], test["rate"], test["term"])
        assert calculated_pmt == test["expected_pmt"]


def test_get_curr_interest_payment():
    tests = [
        {
            "remaining_balance": 0,
            "rate": 50,
            "expected_interest_payment": 0
        },
        {
            "remaining_balance": 50000000,
            "rate": 475,
            "expected_interest_payment": 197917
        },
        {
            "remaining_balance": 12288888,
            "rate": 901,
            "expected_interest_payment": 92269
        },
        {
            "remaining_balance": 70000,
            "rate": 200,
            "expected_interest_payment": 117
        }
    ]
    for test in tests:
        calculated_interest_payment: int = get_curr_interest_payment(test["remaining_balance"], test["rate"])
        assert calculated_interest_payment == test["expected_interest_payment"]


def test_get_loan_schedule():
    loan_details = {
        "amount": 10000000,
        "rate": 400,
        "term": 24
    }
    users: List[schemas.User] = []
    db_loan = models.Loan(
        users=users,
        amount=loan_details["amount"],
        rate=loan_details["rate"],
        term=loan_details["term"]
    )
    loan_schedule = get_loan_schedule(loan=db_loan)
    assert loan_schedule[0].month == 1
    assert loan_schedule[0].interest_payment == 33333
    assert loan_schedule[0].principal_payment == 400916
    assert loan_schedule[0].monthly_payment == 434249
    assert loan_schedule[0].remaining_balance == 9599084
    assert loan_schedule[23].month == 24
    assert loan_schedule[23].interest_payment == 1443
    assert loan_schedule[23].principal_payment == 432814
    assert loan_schedule[23].monthly_payment == 434257
    assert loan_schedule[23].remaining_balance == 0


def test_get_loan_summary():
    loan_details = {
        "id": 1,
        "amount": 10000000,
        "rate": 400,
        "term": 24
    }
    users: List[schemas.User] = []
    db_loan = models.Loan(
        id=loan_details["id"],
        users=users,
        amount=loan_details["amount"],
        rate=loan_details["rate"],
        term=loan_details["term"]
    )
    month: int = 20
    loan_summary = get_loan_summary(loan=db_loan, month=month)
    assert loan_summary.loan_id == 1
    assert loan_summary.month == 20
    assert loan_summary.principal_balance == 1294117
    assert loan_summary.aggregate_principal_paid == 8304967
    assert loan_summary.aggregate_interest_paid == 380013
