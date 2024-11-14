from sqlalchemy import TIMESTAMP, BigInteger, Column, Enum, ForeignKey, Integer

from app.store.database import BaseModel
from app.web.enums import GamesStatusEnum, UserLevelEnum


class GameModel(BaseModel):
    __tablename__ = "games"

    id = Column(BigInteger, primary_key=True, index=True)
    group_id = Column(BigInteger, nullable=False)
    master_id = Column(Integer, ForeignKey("users.id"))
    theme_id = Column(Integer, ForeignKey("themes.id"))
    status = Column(Enum(GamesStatusEnum), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)


class UserStateModel(BaseModel):
    __tablename__ = "user_states"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    score = Column(Integer, default=0)
    mistakes = Column(Integer, default=0)
    level = Column(Enum(UserLevelEnum), nullable=False)
