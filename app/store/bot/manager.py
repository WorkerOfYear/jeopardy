import asyncio
import typing
from datetime import datetime, timedelta
from logging import getLogger

from app.store.telegram_api.dataclasses import Update, Message, CallbackUpdate
from app.web.enums import GamesStatusEnum

if typing.TYPE_CHECKING:
    from app.web.app import Application


THEME_PREFIX = "Тема: "


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")


    async def updates_handler(self, updates: list[Update, CallbackUpdate]):
        for update in updates:
            if isinstance(update, Update) and update.message and update.message.text:
                await self.handle_command(update)
            elif isinstance(update, CallbackUpdate):
                await self.handle_callback(update)


    async def handle_command(self, update: Update):
        if update.message.text == "/start":
            await self.send_message(
                text="Добро пожаловать в Jeopardy!",
                chat_id=update.message.chat.id,
                reply_markup=self.app.store.tg_api.create_inline(
                    text="Начать игру",
                    data="init_game"
                )
            )
        elif update.message.text == "/settings":
            await self.send_message(
                text="Это меню настроек",
                chat_id=update.message.chat.id,
            )
        elif THEME_PREFIX in update.message.text:
            await self.handle_theme_select(update)


    async def handle_callback(self, update: CallbackUpdate):
        if update.data == "init_game":
            await self.init_game(update)


    async def send_message(self, text: str, chat_id: int, reply_markup: dict | None = None) -> int:
        if reply_markup is None:
            reply_markup = {}
        return await self.app.store.tg_api.send_message(
            Message(
                text=text,
                chat_id=chat_id,
                reply_markup=reply_markup
            )
        )


    async def init_game(self, update: CallbackUpdate):
        user = await self.app.store.user.get_user_by_telegram_id(update.user.id)
        if user is None:
            user = await self.app.store.user.create_user(update.user.id, update.user.username)

        if await self.app.store.game.check_game_in_chat(update.chat.id, (GamesStatusEnum.START, GamesStatusEnum.ACTIVE)):
            await self.send_message(
                text=f"Чтобы начать новую игру - закончите прошлую",
                chat_id=update.chat.id,
            )
            return

        game = await self.app.store.game.create_game(group_id=update.chat.id, master_id=user.id)
        await self.app.store.game.create_user_state(user_id=user.id, game_id=game.id)

        themes = await self.app.store.quiz.list_themes()
        buttons = [[{"text": THEME_PREFIX + theme.title}] for theme in themes]
        keyboard = {
            "keyboard": buttons,
            "one_time_keyboard": True,
            "resize_keyboard": True,
            "selective": True,
        }

        await self.send_message(
            text=f"Мастер игры @{update.user.username} выбирает тему..",
            chat_id=update.chat.id,
            reply_markup=keyboard
        )


    async def handle_theme_select(self, update: Update):
        if not await self.app.store.game.check_game_in_chat(update.message.chat.id, (GamesStatusEnum.START,)):
            return

        if not await self.app.store.quiz.check_theme_exists(update.message.text.replace(THEME_PREFIX, "")):
            return

        await self.send_message(
            text="Тема выбрана!",
            chat_id=update.message.chat.id,
            reply_markup={
                "remove_keyboard": True,
            }
        )

        await self.send_message(
            text="Кто будет учавствовать?",
            chat_id=update.message.chat.id,
            reply_markup=self.app.store.tg_api.create_inline(
                text="Учавствовать",
                data="start_game"
            )
        )

        seconds = 30
        text = f"Игра начинается через {seconds}с.."

        message_id = await self.send_message(
            text=text,
            chat_id=update.message.chat.id,
        )

        end_time = datetime.now() + timedelta(seconds=seconds)

        while datetime.now() < end_time:
            remaining_time = end_time - datetime.now()
            text = f"Игра начинается через {round(remaining_time.seconds, 1)}с.."
            await self.app.store.tg_api.edit_message(
                Message(
                    text=text,
                    chat_id=update.message.chat.id,
                    reply_markup={}
                ),
                message_id=message_id
            )
            await asyncio.sleep(1)

        await self.app.store.tg_api.edit_message(
            Message(
                text="Игра началась! 🚀",
                chat_id=update.message.chat.id,
                reply_markup={}
            ),
            message_id=message_id
        )