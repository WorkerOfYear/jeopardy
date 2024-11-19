import typing
from collections.abc import Sequence
from venv import logger

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.quiz.models import ThemeModel, QuestionModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class QuizAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)

    async def get_theme_by_id(self, id_: int) -> ThemeModel | None:
        stmt = select(ThemeModel).where(ThemeModel.id == id_)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first()

    async def list_themes(self) -> Sequence[ThemeModel]:
        stmt = select(ThemeModel)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return [ThemeModel(id=row.id, title=row.title, description=row.description) for row in res.scalars()]

    async def list_questions_by_theme(self, theme_id) -> Sequence[QuestionModel]:
        stmt = select(QuestionModel).where(QuestionModel.theme_id == theme_id)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return [QuestionModel(id=row.id, title=row.title, level=row.level) for row in res.scalars()]

    async def check_theme_exists(self, title: str) -> bool:
        stmt = select(ThemeModel).where(ThemeModel.title == title)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            await session.commit()
            if res.scalars().first() is not None:
                return True
            return False