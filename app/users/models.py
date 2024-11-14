from sqlalchemy import TIMESTAMP, BigInteger, Column, Integer, String

from app.store.database import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String)
    wins = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, nullable=False)
