from sqlalchemy import (
    Enum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database import BaseModel
from app.web.enums import QuestionLevelEnum


class ThemeModel(BaseModel):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class AnswerModel(BaseModel):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)


class QuestionModel(BaseModel):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[int] = mapped_column(
        ForeignKey("themes.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    level: Mapped["QuestionLevelEnum"] = mapped_column(
        Enum(QuestionLevelEnum), nullable=False
    )

    answers: Mapped[list[AnswerModel]] = relationship(
        AnswerModel, uselist=True, lazy="noload"
    )
