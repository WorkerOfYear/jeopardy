import typing

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.store.telegram_api.dataclasses import Update, UpdateMessage, Message, UpdateChat, CallbackUpdate, UpdateUser
from app.store.telegram_api.poller import Poller
from app.web.utils import make_url

if typing.TYPE_CHECKING:
    from app.web.app import Application


API_PATH = "https://api.telegram.org/"


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.poller: Poller | None = None
        self.session: ClientSession | None = None
        self.offset: int = 0


    async def connect(self, app: "Application") -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        self.poller.start()


    async def disconnect(self, app: "Application") -> None:
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()


    def _build_query(self, method: str, params: dict | None = None) -> str:
        if params is None:
            params = {}
        return make_url(API_PATH, f"bot{self.app.config.bot.token}", method, **params)


    @staticmethod
    def get_username(update: dict) -> str:
        try:
            return update["callback_query"]["from"]["username"]
        except KeyError:
            username: str = update["callback_query"]["from"]["first_name"] + update["callback_query"]["from"]["last_name"]
            return username.strip()


    async def poll(self) -> None:
        async with self.session.get(
            self._build_query(
                method="getUpdates",
                params={
                    "offset": self.offset,
                    "timeout": 10,
                    "allowed_updates": ["message", "callback_query"]
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)
            updates = []
            for update in data.get("result", []):
                self.offset = update["update_id"] + 1

                if "message" in update:
                    updates.append(
                        Update(
                            update_id=update["update_id"],
                            message=UpdateMessage(
                                message_id=update["message"]["message_id"],
                                text=update["message"]["text"],
                                chat=UpdateChat(
                                    id=update["message"]["chat"]["id"]
                                )
                            ),
                            user=UpdateUser(
                                id=update["message"]["from"]["id"],
                                username=update["message"]["from"]["username"]
                            )
                        )
                    )
                elif "callback_query" in update:
                    updates.append(
                        CallbackUpdate(
                            data=update["callback_query"]["data"],
                            chat=UpdateChat(
                                id=update["callback_query"]["message"]["chat"]["id"],
                            ),
                            user=UpdateUser(
                                id=update["callback_query"]["from"]["id"],
                                username=self.get_username(update),
                            )
                        )
                    )
            await self.app.store.bot.updates_handler(updates)


    async def send_message(self, message: Message) -> int:
        async with self.session.post(
            self._build_query("sendMessage"),
            json={
                "chat_id": message.chat_id,
                "text": message.text,
                "reply_markup": message.reply_markup
            }
        ) as response:
            data = await response.json()
            self.logger.info(data)
            return data["result"]["message_id"]


    async def edit_message(self, message: Message, message_id: int) -> int:
        async with self.session.post(
            self._build_query("editMessageText"),
            json={
                "chat_id": message.chat_id,
                "text": message.text,
                "message_id": message_id,
            }
        ) as response:
            data = await response.json()
            self.logger.info(data)
            return data["result"]["message_id"]


    @staticmethod
    def create_inline(text: str, data: str) -> dict:
        return {
            "inline_keyboard": [
                [{"text": text, "callback_data": data}],
            ]
        }
