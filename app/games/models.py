from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.store.database import BaseModel
from app.web.enums import GamesStatusEnum, UserLevelEnum


class GameModel(BaseModel):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(nullable=False)
    master_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    theme_id: Mapped[int] = mapped_column(
        ForeignKey("themes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped["GamesStatusEnum"] = mapped_column(
        Enum(GamesStatusEnum), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class UserStateModel(BaseModel):
    __tablename__ = "user_states"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), primary_key=True
    )
    score: Mapped[int] = mapped_column(default=0, nullable=False)
    mistakes: Mapped[int] = mapped_column(default=0, nullable=False)
    level: Mapped["UserLevelEnum"] = mapped_column(
        Enum(UserLevelEnum), nullable=False
    )
