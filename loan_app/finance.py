from typing import List
from decimal import Decimal
from . import schemas


def get_pmt(principal: int, rate: int, term: int):
    n: int = 12
    r: Decimal = rate / 10000
    pmt_Decimal: Decimal = (
        ( principal * (r/n) )
        /( 1 - ( 1 / ( ( 1 + (r/n) )**term ) ) )
    )
    pmt: int = int(round(pmt_Decimal, 0))
    return pmt


def get_curr_interest_payment(remaining_balance: int, rate: int):
    curr_interest_payment_Decimal: Decimal = Decimal(remaining_balance * rate) / 120000
    curr_interest_payment: int = int(round(curr_interest_payment_Decimal, 0))
    return curr_interest_payment


def get_loan_schedule(loan: schemas.Loan):
    loan_schedule: List[LoanScheduleMonth] = []
    monthly_payment: int = get_pmt(loan.amount, loan.rate, loan.term)
    remaining_balance: int = loan.amount
    for month in range(1, loan.term + 1):
        curr_interest_payment: int = get_curr_interest_payment(remaining_balance, loan.rate)
        curr_principal_payment: int = monthly_payment - curr_interest_payment
        remaining_balance -= curr_principal_payment
        if month == loan.term:
            monthly_payment += remaining_balance
            curr_principal_payment += remaining_balance
            remaining_balance = 0
        curr_schedule_month: schemas.LoanScheduleMonth = schemas.LoanScheduleMonth(
            month=month,
            interest_payment=curr_interest_payment,
            principal_payment=curr_principal_payment,
            monthly_payment=monthly_payment,
            remaining_balance=remaining_balance
        )
        loan_schedule.append(curr_schedule_month)
    return loan_schedule


def get_loan_summary(loan: schemas.Loan, month: int):
    loan_schedule: List[LoanScheduleMonth] = get_loan_schedule(loan)
    remaining_balance = loan_schedule[month].remaining_balance
    principal_payment_sum: int = 0
    interest_payment_sum: int = 0
    for currMonth in range(1, month + 1):
        principal_payment_sum += loan_schedule[currMonth].principal_payment
        interest_payment_sum += loan_schedule[currMonth].interest_payment
    loan_summary: schemas.LoanSummary = schemas.LoanSummary(
        loan_id=loan.id,
        month=month,
        principal_balance=remaining_balance,
        aggregate_principal_paid=principal_payment_sum,
        aggregate_interest_paid=interest_payment_sum
    )
    return loan_summary
