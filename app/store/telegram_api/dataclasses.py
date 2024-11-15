from dataclasses import dataclass


# @dataclass
# class InlineKeyboardButton:
#     text: str
#     callback_data: str
#
#
# @dataclass
# class InlineKeyboardMarkup:
#     inline_keyboard: list[list[InlineKeyboardButton]]


@dataclass
class Message:
    chat_id: int | str
    text: str
    reply_markup: dict


@dataclass
class UpdateChat:
    id: int


@dataclass
class UpdateMessage:
    message_id: int
    text: str
    chat: UpdateChat


@dataclass
class Update:
    update_id: int
    message: UpdateMessage


@dataclass
class CallbackUpdate:
    data: str
    chat: UpdateChat

@dataclass
class TelegramResponse:
    ok: bool
    result: list[Update]
