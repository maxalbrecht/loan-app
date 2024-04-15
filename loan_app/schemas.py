from typing import List, Union
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class LoanBase(BaseModel):
    amount: int
    rate: int
    term: int


class LoanCreate(LoanBase):
    user_ids: List[int] = []
    pass


class Loan(LoanBase):
    id: int
    users: List[User] = []

    class Config:
        from_attributes = True


class LoanScheduleMonth(BaseModel):
    month: int
    interest_payment: int
    principal_payment:int
    monthly_payment: int
    remaining_balance: int


class LoanSummary(BaseModel):
    loan_id: int
    month: int
    principal_balance: int
    aggregate_principal_paid: int
    aggregate_interest_paid: int
