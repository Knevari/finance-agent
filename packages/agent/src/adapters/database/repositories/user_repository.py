from typing import Optional
from src.ports.repositories.user_repository import UserRepository
from src.domain.models import UserInfo
from src.adapters.database.models import DBUser

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

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
