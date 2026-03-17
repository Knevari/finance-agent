from abc import ABC, abstractmethod
from typing import Any, Dict, List

class FinancialDataProvider(ABC):
    """
    Abstract base class for financial data providers.
    This acts as a broker between the LangChain agent and the specific 
    provider implementation (like Pluggy).
    """

    @abstractmethod
    def create_connect_token(self, client_user_id: str) -> Dict[str, Any]:
        """
        Create a connection token to initialize the flow 
        for an end-user to connect their bank.
        """
        pass

    @abstractmethod
    def get_accounts(self, item_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all bank accounts associated with a specific connection/item.
        """
        pass

    @abstractmethod
    def get_transactions(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all transactions for a specific bank account.
        """
        pass
