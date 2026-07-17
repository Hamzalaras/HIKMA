"""Inline keyboard builders for Telegram conversations and pagination."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..constants import CallbackData, PAGINATION_LABEL_NEXT, PAGINATION_LABEL_PREVIOUS

DEFAULT_COLUMNS: Final[int] = 2
SKIP_LABEL: Final[str] = "تخطي"


def _chunk_buttons(buttons: Sequence[InlineKeyboardButton], columns: int) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []
    for index in range(0, len(buttons), columns):
        rows.append(list(buttons[index : index + columns]))
    return rows


def build_choice_keyboard(
    field_key: str,
    options: Sequence[tuple[str, str]],
    *,
    columns: int = DEFAULT_COLUMNS,
    include_skip: bool = True,
) -> InlineKeyboardMarkup:
    """Build a keyboard for selecting a predefined option."""

    buttons = [
        InlineKeyboardButton(
            text=label,
            callback_data=f"{CallbackData.FLOW_PREFIX}:{CallbackData.CHOICE_PREFIX}:{field_key}:{value}",
        )
        for label, value in options
    ]
    rows = _chunk_buttons(buttons, columns) if buttons else []

    if include_skip:
        rows.append(
            [
                InlineKeyboardButton(
                    text=SKIP_LABEL,
                    callback_data=f"{CallbackData.FLOW_PREFIX}:{CallbackData.SKIP_PREFIX}:{field_key}",
                )
            ]
        )

    return InlineKeyboardMarkup(rows)


def build_skip_keyboard(field_key: str) -> InlineKeyboardMarkup:
    """Build a keyboard with only the skip action."""

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=SKIP_LABEL, callback_data=f"{CallbackData.FLOW_PREFIX}:{CallbackData.SKIP_PREFIX}:{field_key}")]]
    )


def build_lines_pagination_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup | None:
    """Build previous/next controls for the /lines flow."""

    buttons: list[InlineKeyboardButton] = []

    if page > 1:
        buttons.append(
            InlineKeyboardButton(
                text=PAGINATION_LABEL_PREVIOUS,
                callback_data=CallbackData.LINES_PREVIOUS,
            )
        )

    if page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text=PAGINATION_LABEL_NEXT,
                callback_data=CallbackData.LINES_NEXT,
            )
        )

    if not buttons:
        return None

    return InlineKeyboardMarkup([buttons])
