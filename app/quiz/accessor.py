import typing
from collections.abc import Sequence

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.quiz.models import QuestionModel, ThemeModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class QuizAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)

    async def get_theme_by_title(self, title: str) -> ThemeModel | None:
        stmt = select(ThemeModel).where(ThemeModel.title == title)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first()

    async def get_theme_by_id(self, theme_id: int) -> ThemeModel | None:
        stmt = select(ThemeModel).where(ThemeModel.id == theme_id)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first()

    async def list_themes(self) -> Sequence[ThemeModel]:
        stmt = select(ThemeModel)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().all()

    async def list_questions_by_theme(
        self, theme_id: int
    ) -> Sequence[QuestionModel]:
        stmt = select(QuestionModel).where(QuestionModel.theme_id == theme_id)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().all()

    async def check_theme_exists(self, title: str) -> bool:
        stmt = select(ThemeModel).where(ThemeModel.title == title)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first() is not None
