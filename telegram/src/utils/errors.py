"""Custom exception hierarchy for the Hikma Telegram bot."""

from __future__ import annotations


class HikmaError(Exception):
    """Base exception for all bot-specific failures."""

    __slots__ = ("message", "user_message")

    def __init__(self, message: str, user_message: str) -> None:
        super().__init__(message)
        self.message = message
        self.user_message = user_message


class ApiError(HikmaError):
    """Raised when the API returns an invalid or unexpected response."""

    def __init__(self, message: str, user_message: str = "حدث خطأ في بيانات الخدمة.") -> None:
        super().__init__(message=message, user_message=user_message)


class ApiNetworkError(ApiError):
    """Raised when the HTTP transport fails before receiving a response."""

    def __init__(self, message: str = "Network request to API failed.") -> None:
        super().__init__(
            message=message,
            user_message="تعذر الاتصال بالخدمة حالياً. حاول مرة أخرى بعد قليل.",
        )


class ApiTimeoutError(ApiNetworkError):
    """Raised when the HTTP request exceeds the configured timeout."""

    def __init__(self, message: str = "API request timed out.") -> None:
        super().__init__(message=message)
        self.user_message = "انتهت مهلة الاتصال بالخدمة. حاول مرة أخرى بعد قليل."


class ApiResponseError(ApiError):
    """Raised when the API response is malformed or structurally invalid."""

    def __init__(self, message: str = "API response was malformed.") -> None:
        super().__init__(message=message, user_message="استلمنا استجابة غير صالحة من الخدمة.")


class ApiNotFoundError(ApiError):
    """Raised when the API does not contain a matching record."""

    def __init__(self, message: str = "Requested resource was not found.") -> None:
        super().__init__(message=message, user_message="لم يتم العثور على بيانات مطابقة لبحثك.")
