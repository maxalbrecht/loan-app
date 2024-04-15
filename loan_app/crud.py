from typing import List
from sqlalchemy.orm import Session
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_loans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Loan).offset(skip).limit(limit).all()


def get_loan(db:Session, loan_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()


def get_user_loans(db:Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Loan).filter(models.Loan.users.any(models.User.id == user_id)).offset(skip).limit(limit).all()


def create_user_loan(db:Session, loan_create: schemas.LoanCreate):
    user_ids = loan_create.user_ids
    db_users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    db_loan = models.Loan(
        amount=loan_create.amount,
        rate=loan_create.rate,
        term=loan_create.term,
        users=db_users
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan
