from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.adapters.database.models import Base

class Database:
    def __init__(self, connection_string: str = "sqlite:///finance_agent.db"):
        self.engine = create_engine(connection_string, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
