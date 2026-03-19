from abc import ABC, abstractmethod
from typing import List
from ..models.transaction import TransactionInfo

class TransactionsRepository(ABC):
    @abstractmethod
    def save_transactions(self, transactions: List[TransactionInfo]) -> None:
        pass
        
    @abstractmethod
    def get_transactions_by_account(self, account_id: str) -> List[TransactionInfo]:
        pass