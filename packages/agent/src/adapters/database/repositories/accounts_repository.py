from typing import List
from src.ports.repositories.accounts_repository import AccountsRepository
from src.domain.models import AccountInfo
from src.adapters.database.models import DBAccount

class SQLAlchemyAccountsRepository(AccountsRepository):
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

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
