import typing

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.store.telegram_api.dataclasses import Update, UpdateMessage, Message, UpdateChat, CallbackUpdate
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

    def _build_query(self, method: str, params: dict) -> str:
        return make_url(API_PATH, f"bot{self.app.config.bot.token}", method, **params)

    async def poll(self) -> None:
        async with self.session.get(
            self._build_query(
                method="getUpdates",
                params={
                    "offset": self.offset,
                    "timeout": 10
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)
            updates = []
            for update in data.get("result", []):
                self.offset = update["update_id"] + 1

                if "callback_query" not in update:
                    updates.append(
                        Update(
                            update_id=update["update_id"],
                            message=UpdateMessage(
                                message_id=update["message"]["message_id"],
                                text=update["message"]["text"],
                                chat=UpdateChat(
                                    id=update["message"]["chat"]["id"]
                                )
                            )
                        )
                    )
                else:
                    updates.append(
                        CallbackUpdate(
                            data=update["callback_query"]["data"],
                            chat=UpdateChat(
                                update["callback_query"]["message"]["chat"]["id"]
                            )
                        )
                    )
            await self.app.store.bot.updates_handler(updates)


    async def send_message(self, message: Message) -> None:
        async with self.session.post(
            self._build_query(
                "sendMessage",
                params={},
            ),
            json={
                "chat_id": message.chat_id,
                "text": message.text,
                "reply_markup": message.reply_markup
            }
        ) as response:
            data = await response.json()
            self.logger.info(data)
