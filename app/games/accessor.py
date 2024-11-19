import typing

from sqlalchemy import insert, select

from app.base.base_accessor import BaseAccessor
from app.games.models import GameModel, UserStateModel
from app.web.enums import GamesStatusEnum, UserLevelEnum

if typing.TYPE_CHECKING:
    from app.web.app import Application


class GameAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)

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

    async def check_game_in_chat(self, group_id, states: tuple[GamesStatusEnum, ...]) -> bool:
        stmt = (select(GameModel)
                .where(GameModel.group_id == group_id)
                .where(GameModel.status.in_(states)))

        async with self.app.database.session() as session:
            res = await session.execute(stmt)
            await session.commit()
            if res.scalars().first() is not None:
                return True
            return False