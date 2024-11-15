import typing
from logging import getLogger

from app.store.telegram_api.dataclasses import Update, Message, CallbackUpdate

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")

    async def updates_handler(self, updates: list[Update, CallbackUpdate]):
        for update in updates:
            if isinstance(update, Update) and update.message and update.message.text:
                await self.check_command(update.message.text, update.message.chat.id)
            elif isinstance(update, CallbackUpdate):
                self.logger.info("Callback")

    async def check_command(self, text: str, chat_id: int):
        if text == "/start":
            await self.app.store.tg_api.send_message(
                Message(
                    text="Добро пожаловать!",
                    chat_id=chat_id,
                    reply_markup={}
                )
            )
        elif text == "/settings":
            await self.app.store.tg_api.send_message(
                Message(
                    text="Это меню настроек",
                    chat_id=chat_id,
                    reply_markup={
                        "inline_keyboard": [
                            [{"text": "Начать игру", "callback_data": "start_game"}],
                        ]
                    }
                )
            )
