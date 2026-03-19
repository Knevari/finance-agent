from abc import ABC, abstractmethod
from typing import Optional
from ..models.user import UserInfo

class UserRepository(ABC):
    """Abstract interface for persisting users"""

    @abstractmethod
    def get_user_by_client_id(self, client_user_id: str) -> Optional[UserInfo]:
        pass

    @abstractmethod
    def save_user_item(self, client_user_id: str, pluggy_item_id: str) -> UserInfo:
        pass