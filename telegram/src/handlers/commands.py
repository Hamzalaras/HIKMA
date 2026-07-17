"""Command and conversation handler factories for the Telegram bot."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters

from ..constants import CallbackData, COMMAND_NAMES, HELP_TEXT, START_TEXT
from ..services.client import KatherApiClient
from .definitions import FLOW_DEFINITIONS
from .flow import FlowState, cancel_flow, handle_choice_callback, handle_skip, handle_text_input, start_flow


def _make_entry_handler(flow_name: str) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Any]:
    async def _entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await start_flow(update, context, flow_name)

    return _entry


def build_conversation_handler(flow_name: str, client: KatherApiClient) -> ConversationHandler:
    """Build a conversation handler for a specific command flow."""

    definition = FLOW_DEFINITIONS[flow_name]
    entry_handler = CommandHandler(flow_name, _make_entry_handler(flow_name))

    return ConversationHandler(
        entry_points=[entry_handler],
        states={
            FlowState.COLLECTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input),
                CallbackQueryHandler(handle_choice_callback, pattern=f"^{CallbackData.FLOW_PREFIX}:(?:{CallbackData.CHOICE_PREFIX}|{CallbackData.SKIP_PREFIX}):"),
                CommandHandler(COMMAND_NAMES["SKIP"], handle_skip),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_flow)],
        name=f"{definition.name}_conversation",
        persistent=False,
        allow_reentry=True,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send the bot introduction and available command summary."""

    message = update.effective_message
    if message is None:
        return ConversationHandler.END

    await message.reply_text(text=START_TEXT, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send the bot help text."""

    message = update.effective_message
    if message is None:
        return ConversationHandler.END

    await message.reply_text(text=HELP_TEXT, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def build_command_handlers(client: KatherApiClient) -> list[ConversationHandler]:
    """Build the four command conversation handlers."""

    return [
        build_conversation_handler("line", client),
        build_conversation_handler("lines", client),
        build_conversation_handler("poem", client),
        build_conversation_handler("poet", client),
    ]
