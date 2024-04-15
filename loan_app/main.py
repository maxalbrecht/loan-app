from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas, finance
from .database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "loan_app"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/loans/", response_model=schemas.Loan)
def create_loan_for_user(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    if len(loan.user_ids) < 1:
        raise HTTPException(status_code=400, detail="No user_ids provided")
    for user_id in loan.user_ids:
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
    return crud.create_user_loan(db=db, loan_create=loan)


@app.get("/loans/", response_model=List[schemas.Loan])
def read_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    loans = crud.get_loans(db, skip=skip, limit=limit)
    return loans


@app.get("/loans/{loan_id}", response_model=schemas.Loan)
def read_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = crud.get_loan(db, loan_id = loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return db_loan


@app.get("/loans/{loan_id}/schedule", response_model=List[schemas.LoanScheduleMonth])
def read_loan_schedule(loan_id: int, db: Session = Depends(get_db)):
    db_loan = crud.get_loan(db, loan_id = loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    loan_schedule = finance.get_loan_schedule(loan=db_loan)
    return loan_schedule


@app.get("/users/{user_id}/loans", response_model=List[schemas.Loan])
def read_loans_for_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_loans = crud.get_user_loans(db, user_id = user_id)
    return db_loans


@app.get("/loans/{loan_id}/summary", response_model=schemas.LoanSummary)
def read_loan_summary(loan_id: int, month: int, db: Session = Depends(get_db)):
    db_loan = crud.get_loan(db, loan_id = loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if month > db_loan.term:
        raise HTTPException(status_code=400, detail="Month higher than loan term")
    loan_summary = finance.get_loan_summary(loan=db_loan, month=month)
    return loan_summary
