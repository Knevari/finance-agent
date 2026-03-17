from typing import Optional, List
from sqlalchemy import create_engine, Column, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from src.ports.database_repository import DatabaseRepository
from src.domain.models import UserInfo, AccountInfo, TransactionInfo

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


class SQLAlchemyAdapter(DatabaseRepository):
    def __init__(self, connection_string: str = "sqlite:///finance_agent.db"):
        self.engine = create_engine(connection_string, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_user_by_client_id(self, client_user_id: str) -> Optional[UserInfo]:
        with self.SessionLocal() as session:
            user = session.query(DBUser).filter(DBUser.client_user_id == client_user_id).first()
            if user:
                return UserInfo(client_user_id=user.client_user_id, pluggy_item_id=user.pluggy_item_id)
        return None

    def save_user_item(self, client_user_id: str, pluggy_item_id: str) -> UserInfo:
        with self.SessionLocal() as session:
            user = session.query(DBUser).filter(DBUser.client_user_id == client_user_id).first()
            if not user:
                user = DBUser(client_user_id=client_user_id, pluggy_item_id=pluggy_item_id)
                session.add(user)
            else:
                user.pluggy_item_id = pluggy_item_id
            session.commit()
            return UserInfo(client_user_id=user.client_user_id, pluggy_item_id=user.pluggy_item_id)

    def save_accounts(self, accounts: List[AccountInfo]) -> None:
        with self.SessionLocal() as session:
            for acc in accounts:
                db_acc = session.query(DBAccount).filter(DBAccount.id == acc.id).first()
                if not db_acc:
                    db_acc = DBAccount(
                        id=acc.id, item_id=acc.item_id, name=acc.name, 
                        type=acc.type, balance=acc.balance
                    )
                    session.add(db_acc)
                else:
                    db_acc.balance = acc.balance
            session.commit()

    def get_accounts_by_item(self, pluggy_item_id: str) -> List[AccountInfo]:
        with self.SessionLocal() as session:
            accounts = session.query(DBAccount).filter(DBAccount.item_id == pluggy_item_id).all()
            return [AccountInfo(id=a.id, item_id=a.item_id, name=a.name, type=a.type, balance=a.balance) for a in accounts]

    def save_transactions(self, transactions: List[TransactionInfo]) -> None:
        with self.SessionLocal() as session:
            for t in transactions:
                db_t = session.query(DBTransaction).filter(DBTransaction.id == t.id).first()
                if not db_t:
                    db_t = DBTransaction(
                        id=t.id, account_id=t.account_id, amount=t.amount,
                        date=t.date, description=t.description
                    )
                    session.add(db_t)
            session.commit()

    def get_transactions_by_account(self, account_id: str) -> List[TransactionInfo]:
        with self.SessionLocal() as session:
            transactions = session.query(DBTransaction).filter(DBTransaction.account_id == account_id).all()
            return [TransactionInfo(id=t.id, account_id=t.account_id, amount=t.amount, date=t.date, description=t.description) for t in transactions]

# Default singleton instantiation
db_adapter = SQLAlchemyAdapter()
