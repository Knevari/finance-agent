from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models import UserInfo, AccountInfo, TransactionInfo

class DatabaseRepository(ABC):
    """
    Abstract interface for persisting users, accounts, and transactions.
    """
    
    @abstractmethod
    def get_user_by_client_id(self, client_user_id: str) -> Optional[UserInfo]:
        pass

    @abstractmethod
    def save_user_item(self, client_user_id: str, pluggy_item_id: str) -> UserInfo:
        pass
        
    @abstractmethod
    def save_accounts(self, accounts: List[AccountInfo]) -> None:
        pass
        
    @abstractmethod
    def get_accounts_by_item(self, pluggy_item_id: str) -> List[AccountInfo]:
        pass
        
    @abstractmethod
    def save_transactions(self, transactions: List[TransactionInfo]) -> None:
        pass
        
    @abstractmethod
    def get_transactions_by_account(self, account_id: str) -> List[TransactionInfo]:
        pass
