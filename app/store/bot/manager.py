import asyncio
import typing
from datetime import datetime, timedelta
from logging import getLogger

from app.store.telegram_api.dataclasses import Update, Message, CallbackUpdate
from app.users.models import UserModel
from app.web.enums import GamesStatusEnum

if typing.TYPE_CHECKING:
    from app.web.app import Application


THEME_PREFIX = "Тема: "


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")

    async def updates_handler(self, updates: list[Update, CallbackUpdate]) -> None:
        for update in updates:
            if isinstance(update, Update) and update.message and update.message.text:
                await self.handle_command(update)
            elif isinstance(update, CallbackUpdate):
                await self.handle_callback(update)

    async def handle_command(self, update: Update) -> None:
        if update.message.text == "/start":
            await self.start_command(update)
        elif update.message.text == "/settings":
            await self.settings_command(update)
        elif THEME_PREFIX in update.message.text:
            await self.theme_select(update)

    async def start_command(self, update: Update) -> None:
        await self.send_message(
            text="Добро пожаловать в Jeopardy!",
            chat_id=update.message.chat.id,
            reply_markup=self.app.store.tg_api.create_inline(
                text="Начать игру",
                data="start_game"
            )
        )

    async def settings_command(self, update: Update) -> None:
        await self.send_message(
            text="Это меню настроек",
            chat_id=update.message.chat.id,
        )

    async def handle_callback(self, update: CallbackUpdate) -> None:
        if update.data == "start_game":
            await self.start_game(update)
        elif update.data == "join_game":
            await self.join_game(update)


    async def start_game(self, update: CallbackUpdate) -> None:
        """"Создаёт новую игру, добавляет мастера и запускает выбор темы."""

        user = await self.get_or_create_user(update.user.id, update.user.username)

        if await self.is_game_active(update.chat.id):
            await self.send_message(
                text=f"Чтобы начать новую игру - закончите прошлую",
                chat_id=update.chat.id,
            )
            return

        game = await self.app.store.game.create_game(group_id=update.chat.id, master_id=user.id)
        await self.app.store.game.create_user_state(user_id=user.id, game_id=game.id)

        themes = await self.app.store.quiz.list_themes()
        keyboard = self.create_theme_keyboard(themes)

        await self.send_message(
            text=f"Мастер игры @{update.user.username} выбирает тему..",
            chat_id=update.chat.id,
            reply_markup=keyboard
        )

    async def theme_select(self, update: Update) -> None:
        """"Проверяет тему, добавляет её в игру и вызывает приглашения к участию"""

        game = await self.app.store.game.get_start_game(update.message.chat.id)
        if game is None or game.theme_id is not None:
            return

        theme_title = update.message.text.replace(THEME_PREFIX, "")
        theme = await self.app.store.quiz.get_theme_by_title(theme_title)
        if theme is None:
            return

        await self.app.store.game.add_theme_to_game(
            group_id=update.message.chat.id,
            theme_id=theme.id
        )
        await self.send_message(
            text="Тема выбрана!",
            chat_id=update.message.chat.id,
            reply_markup={
                "remove_keyboard": True,
            }
        )
        asyncio.create_task(self.start_contest(update))

    async def start_contest(self, update: Update) -> None:
        """Отправляет кнопку участия с таймером, затем запускает игру"""

        await self.send_message(
            text="Кто будет учавствовать?",
            chat_id=update.message.chat.id,
            reply_markup=self.app.store.tg_api.create_inline(
                text="Учавствовать",
                data="join_game"
            )
        )
        await self.message_timer(
            chat_id=update.message.chat.id,
            title="Игра начинается",
            final_title="Игра началась! 🚀",
            seconds=20
        )
        await self.app.store.game.activate_game(
            group_id=update.message.chat.id,
        )

    async def join_game(self, update: CallbackUpdate) -> None:
        """Добавляет тех кто нажал 'Учавствовать' в игру"""

        game = await self.app.store.game.get_start_game(update.chat.id)
        if game is None:
            return

        user = await self.app.store.user.get_user_by_telegram_id(update.user.id)
        if user is None:
            user = await self.app.store.user.create_user(update.user.id, update.user.username)

        if await self.app.store.game.check_user_state(user_id=user.id, game_id=game.id):
            return
        await self.app.store.game.create_user_state(user_id=user.id, game_id=game.id)
        await self.send_message(chat_id=update.chat.id, text=f"@{user.username} присоединяется к игре")

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

    async def edit_message(self, text: str, chat_id: int, message_id: int, reply_markup: dict | None = None) -> int:
        if reply_markup is None:
            reply_markup = {}
        return await self.app.store.tg_api.edit_message(
            Message(
                text=text,
                chat_id=chat_id,
                reply_markup=reply_markup
            ),
            message_id=message_id
        )

    async def message_timer(self, chat_id: int, title: str, final_title: str, seconds: int) -> None:
        text = f"{title}, осталось {seconds}с"
        message_id = await self.send_message(
            text=text,
            chat_id=chat_id,
        )
        end_time = datetime.now() + timedelta(seconds=seconds)
        while datetime.now() < end_time:
            remaining_time = end_time - datetime.now()
            text = f"{title}, осталось {round(remaining_time.seconds, 1)}с.."
            await self.edit_message(
                text=text,
                chat_id=chat_id,
                message_id=message_id
            )
            await asyncio.sleep(1)

        await self.edit_message(
            text=final_title,
            chat_id=chat_id,
            message_id=message_id
        )

    async def get_or_create_user(self, telegram_id: int, username: str) -> UserModel:
        user = await self.app.store.user.get_user_by_telegram_id(telegram_id)
        if not user:
            user = await self.app.store.user.create_user(telegram_id, username)
        return user

    async def is_game_active(self, group_id: int) -> bool:
        return await self.app.store.game.check_game_in_chat(
            group_id=group_id,
            states=(GamesStatusEnum.START, GamesStatusEnum.ACTIVE)
        )

    @staticmethod
    def create_theme_keyboard(themes) -> dict:
        buttons = [[{"text": THEME_PREFIX + theme.title}] for theme in themes]
        return {
            "keyboard": buttons,
            "one_time_keyboard": True,
            "resize_keyboard": True,
            "selective": True,
        }