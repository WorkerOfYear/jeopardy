import typing

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.games.models import GameModel, UserStateModel
from app.web.enums import GamesStatusEnum, UserLevelEnum

if typing.TYPE_CHECKING:
    from app.web.app import Application


class GameAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)

    @staticmethod
    async def execute_get_start_game(group_id: int, session: AsyncSession) -> GameModel | None:
        stmt = (select(GameModel)
                .where(GameModel.group_id == group_id)
                .where(GameModel.status == GamesStatusEnum.START))
        res = await session.execute(stmt)
        return res.scalars().one_or_none()

    async def create_game(self, group_id: int, master_id: int) -> GameModel:
        new_game = GameModel(
            group_id=group_id,
            master_id=master_id,
            theme_id=None,
            status=GamesStatusEnum.START,
            start_time=None,
            end_time=None,
        )
        async with self.app.database.session() as session:
            session.add(new_game)
            await session.commit()

        return new_game

    async def create_user_state(self, user_id, game_id) -> UserStateModel:
        new_user_state = UserStateModel(
            user_id=user_id,
            game_id=game_id,
            level=UserLevelEnum.GREEN,
        )
        async with self.app.database.session() as session:
            session.add(new_user_state)
            await session.commit()

        return new_user_state

    async def check_user_state(self, user_id, game_id) -> bool:
        stmt = (select(UserStateModel)
                .where(UserStateModel.user_id == user_id)
                .where(UserStateModel.game_id == game_id))
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().one_or_none() is not None

    async def get_start_game(self, group_id) -> GameModel | None:
        async with self.app.database.session() as session:
            return await self.execute_get_start_game(group_id, session)

    async def check_game_in_chat(self, group_id, states: tuple[GamesStatusEnum, ...]) -> bool:
        stmt = (select(GameModel)
                .where(GameModel.group_id == group_id)
                .where(GameModel.status.in_(states)))
        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            return res.scalars().one_or_none() is not None

    async def add_theme_to_game(self, group_id: int, theme_id: int) -> None:
        async with self.app.database.session() as session:
            game = await self.execute_get_start_game(group_id, session)
            upd = update(GameModel).where(GameModel.id == game.id).values(theme_id=theme_id)
            await session.execute(upd)
            await session.commit()

    async def activate_game(self, group_id: int ) -> None:
        async with self.app.database.session() as session:
            game = await self.execute_get_start_game(group_id, session)
            upd = update(GameModel).where(GameModel.id == game.id).values(status=GamesStatusEnum.ACTIVE)
            await session.execute(upd)
            await session.commit()
