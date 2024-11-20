import asyncio
import typing
from asyncio import Task

if typing.TYPE_CHECKING:
    from app.store import Store


class Poller:
    def __init__(self, store: "Store") -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    def start(self) -> None:
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self) -> None:
        self.is_running = False
        await self.poll_task

    async def poll(self) -> None:
        while self.is_running:
            await self.store.tg_api.poll()
