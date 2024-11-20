import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass(kw_only=True, slots=True)
class SessionConfig:
    key: str


@dataclass(kw_only=True, slots=True)
class BotConfig:
    token: str


@dataclass(kw_only=True, slots=True)
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


@dataclass(kw_only=True, slots=True)
class Config:
    session: SessionConfig | None = None
    bot: BotConfig | None = None
    database: DatabaseConfig | None = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        session=SessionConfig(
            key=raw_config["session"]["key"],
        ),
        bot=BotConfig(
            token=raw_config["bot"]["token"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
    )
