"""Telegram handler factory exports."""

from __future__ import annotations

from typing import Any

from telegram.ext import CallbackQueryHandler, CommandHandler

from ..services.client import KatherApiClient
from .callbacks import handle_lines_pagination
from .commands import build_command_handlers, help_command, start_command


def build_handlers(client: KatherApiClient) -> list[Any]:
    """Build all handlers required by the Telegram bot."""

    handlers: list[Any] = []
    handlers.append(CommandHandler("start", start_command))
    handlers.append(CommandHandler("help", help_command))
    handlers.extend(build_command_handlers(client))
    handlers.append(CallbackQueryHandler(handle_lines_pagination, pattern="^(lines:prev|lines:next)$"))
    return handlers
