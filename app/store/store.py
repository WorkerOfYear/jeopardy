import typing

from app.store.bot.manager import BotManager
from app.store.database import Database
from app.store.telegram_api.accessor import TgApiAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.users.accessor import UserAccessor
        from app.quiz.accessor import QuizAccessor
        from app.games.accessor import GameAccessor

        self.user = UserAccessor(app)
        self.quiz = QuizAccessor(app)
        self.game = GameAccessor(app)
        self.tg_api = TgApiAccessor(app)
        self.bot = BotManager(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
