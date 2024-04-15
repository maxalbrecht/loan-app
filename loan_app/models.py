from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from .database import Base


class UserLoan(Base):
    __tablename__ = "user_loan"
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    loan_id = Column('loan_id', Integer, ForeignKey('loans.id'))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    loans = relationship("Loan", secondary='user_loan', back_populates="users")


class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    rate = Column(Integer)
    term = Column(Integer)
    users = relationship("User", secondary='user_loan', back_populates="loans")
