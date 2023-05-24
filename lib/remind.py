import re
import pytz


class Remind:
    def __init__(self) -> None:
        pass

    def validate_time(expression: str) -> bool:
        """
        >>> Remind.validate_time("")
        False
        >>> Remind.validate_time("foo")
        False
        >>> Remind.validate_time("bar:baz")
        False
        >>> Remind.validate_time("24:60")
        False
        >>> Remind.validate_time("00:00")
        True
        >>> Remind.validate_time("12:05")
        True
        >>> Remind.validate_time("23:59")
        True
        """
        return bool(re.fullmatch(r"^(0?[0-9]|1[0-9]|2[0-3]):(0?[0-9]|[1-5][0-9])$", expression))

    def validate_tz(candidate: str) -> bool:
        """
        >>> Remind.validate_tz("")
        False
        >>> Remind.validate_tz("foo")
        False
        >>> Remind.validate_tz("UTC")
        True
        >>> Remind.validate_tz("Europe/Moscow")
        True
        """
        try:
            pytz.timezone(candidate)
        except Exception:
            return False
        return True
