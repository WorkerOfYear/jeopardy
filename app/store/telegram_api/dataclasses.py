from dataclasses import dataclass


@dataclass(kw_only=True, slots=True)
class Message:
    chat_id: int | str
    text: str
    reply_markup: dict


@dataclass(kw_only=True, slots=True)
class UpdateUser:
    id: int
    username: str


@dataclass(kw_only=True, slots=True)
class UpdateChat:
    id: int


@dataclass(kw_only=True, slots=True)
class UpdateMessage:
    message_id: int
    text: str
    chat: UpdateChat


@dataclass(kw_only=True, slots=True)
class Update:
    update_id: int
    message: UpdateMessage
    user: UpdateUser


@dataclass(kw_only=True, slots=True)
class CallbackUpdate:
    data: str
    chat: UpdateChat
    user: UpdateUser
