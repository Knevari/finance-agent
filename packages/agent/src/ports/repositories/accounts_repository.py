from abc import ABC, abstractmethod
from typing import List
from ..models.account import AccountInfo

class AccountsRepository(ABC):
    @abstractmethod
    def save_accounts(self, accounts: List[AccountInfo]) -> None:
        pass
        
    @abstractmethod
    def get_accounts_by_item(self, pluggy_item_id: str) -> List[AccountInfo]:
        pass