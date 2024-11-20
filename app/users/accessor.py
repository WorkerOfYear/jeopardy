import typing
from datetime import UTC, datetime

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.users.models import UserModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class UserAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)

    async def create_user(
        self, telegram_id: int, username: str | None = None
    ) -> UserModel:
        new_user = UserModel(
            telegram_id=telegram_id,
            username=username,
            wins=0,
            created_at=datetime.now(UTC),
        )
        async with self.app.database.session() as session:
            session.add(new_user)
            await session.commit()

        return new_user

    async def check_user(self, telegram_id: int) -> bool:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first() is not None

    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first()
