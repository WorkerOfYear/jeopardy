from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.store.database import BaseModel
from app.web.enums import QuestionLevelEnum


class ThemeModel(BaseModel):
    __tablename__ = "themes"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(Text)


class AnswerModel(BaseModel):
    __tablename__ = "answers"

    id = Column(BigInteger, primary_key=True, index=True)
    question_id = Column(
        BigInteger,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)


class QuestionModel(BaseModel):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True, index=True)
    theme_id = Column(
        BigInteger, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, unique=True, nullable=False)
    level = Column(Enum(QuestionLevelEnum), nullable=False)

    answers = relationship(AnswerModel, uselist=True)
