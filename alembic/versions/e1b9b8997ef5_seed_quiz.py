"""seed quiz

Revision ID: e1b9b8997ef5
Revises: 1590e596c081
Create Date: 2024-11-15 13:59:37.571409

"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.quiz.model import ThemeModel, QuestionModel, AnswerModel
from app.web.enums import QuestionLevelEnum


# revision identifiers, used by Alembic.
revision: str = 'e1b9b8997ef5'
down_revision: Union[str, None] = '1590e596c081'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


file_path = 'alembic/mock/quiz/data.json'
with open(file_path, 'r', encoding='utf-8') as file:
    themes_data = json.load(file)


engine = create_engine('postgresql+asyncpg://postgres:123@localhost/postgres')
Session = sessionmaker(bind=engine)
session = Session()


def upgrade() -> None:
    for theme_data in themes_data:
        theme = ThemeModel(
            title=theme_data['title'],
            description=theme_data['description']
        )
        session.add(theme)
        session.commit()

        for question_data in theme_data['questions']:
            question = QuestionModel(
                title=question_data['title'],
                level=QuestionLevelEnum[question_data['level'].upper()],
                theme_id=theme.id
            )
            session.add(question)
            session.commit()

            for answer_data in question_data['answers']:
                answer = AnswerModel(
                    title=answer_data['title'],
                    is_correct=answer_data['is_correct'],
                    question_id=question.id
                )
                session.add(answer)

        session.commit()

def downgrade() -> None:
    pass
