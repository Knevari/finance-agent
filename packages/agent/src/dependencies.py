from src.adapters.database.session import Database
from src.adapters.database.repositories.user_repository import SQLAlchemyUserRepository
from src.adapters.database.repositories.accounts_repository import SQLAlchemyAccountsRepository
from src.adapters.database.repositories.transactions_repository import SQLAlchemyTransactionsRepository

# Initialize dependency injection container singletons
db = Database()
user_repository = SQLAlchemyUserRepository(db.SessionLocal)
accounts_repository = SQLAlchemyAccountsRepository(db.SessionLocal)
transactions_repository = SQLAlchemyTransactionsRepository(db.SessionLocal)
