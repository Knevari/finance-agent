from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DBUser(Base):
    __tablename__ = 'users'
    client_user_id = Column(String, primary_key=True)
    pluggy_item_id = Column(String, nullable=True)


class DBAccount(Base):
    __tablename__ = 'accounts'
    id = Column(String, primary_key=True)
    item_id = Column(String, index=True)
    name = Column(String)
    type = Column(String)
    balance = Column(Float)


class DBTransaction(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True)
    account_id = Column(String, index=True)
    amount = Column(Float)
    date = Column(String)
    description = Column(String)
