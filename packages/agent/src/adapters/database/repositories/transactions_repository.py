from typing import List
from src.ports.repositories.transactions_repository import TransactionsRepository
from src.domain.models import TransactionInfo
from src.adapters.database.models import DBTransaction

class SQLAlchemyTransactionsRepository(TransactionsRepository):
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

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
