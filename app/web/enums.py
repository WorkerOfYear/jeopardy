from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(self, item):
        try:
            self(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    pass


class GamesStatusEnum(BaseEnum):
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    CANCELED = "CANCELED"


class UserLevelEnum(BaseEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class QuestionLevelEnum(BaseEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
