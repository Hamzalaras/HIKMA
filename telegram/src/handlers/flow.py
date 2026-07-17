"""Generic conversation flow runtime used by the command handlers."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, Final

from telegram import InlineKeyboardMarkup, Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest, TelegramError

from ..constants import ARABIC_SKIP_COMMAND, CallbackData, ERROR_GENERIC_TEXT, ERROR_NETWORK_TEXT, ERROR_NOT_FOUND_TEXT, SKIP_HINT_TEXT
from ..utils.errors import ApiError, ApiNetworkError, ApiNotFoundError, ApiResponseError, ApiTimeoutError, HikmaError
from ..utils.keyboards import build_choice_keyboard, build_skip_keyboard
from ..utils.messages import RenderedMessage
from .definitions import FLOW_DEFINITIONS
from .states import FlowDefinition, FlowField, FlowSession, FlowState

LOGGER = logging.getLogger(__name__)
FLOW_SESSION_KEY: Final[str] = "hikma_flow_session"
LINES_PAGINATION_KEY: Final[str] = "hikma_lines_pagination"


def _get_definition(flow_name: str) -> FlowDefinition:
    return FLOW_DEFINITIONS[flow_name]


def _get_session(context: ContextTypes.DEFAULT_TYPE) -> FlowSession | None:
    session = context.user_data.get(FLOW_SESSION_KEY)
    return session if isinstance(session, FlowSession) else None


def _set_session(context: ContextTypes.DEFAULT_TYPE, session: FlowSession | None) -> None:
    if session is None:
        context.user_data.pop(FLOW_SESSION_KEY, None)
        return
    context.user_data[FLOW_SESSION_KEY] = session


def _clear_session(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(FLOW_SESSION_KEY, None)


def _get_current_field(session: FlowSession, definition: FlowDefinition) -> FlowField:
    return definition.fields[session.field_index]


def _build_prompt_keyboard(field: FlowField) -> InlineKeyboardMarkup:
    if field.options:
        return build_choice_keyboard(field.key, field.options, include_skip=True)
    return build_skip_keyboard(field.key)


async def _send_prompt(update: Update, text: str, keyboard: InlineKeyboardMarkup | None) -> None:
    message = update.effective_message
    if message is None:
        return

    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.edit_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return
        except BadRequest:
            LOGGER.warning("Prompt message could not be edited; falling back to a new reply.")
        except TelegramError:
            LOGGER.exception("Unexpected Telegram failure while editing prompt message")

    try:
        await message.reply_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    except TelegramError:
        LOGGER.exception("Unable to send fallback prompt message")


async def _send_loading_message(update: Update) -> Message | None:
    """Send the temporary loading message shown while the API request runs."""

    message = update.effective_message
    if message is None:
        return None

    try:
        return await message.reply_text(text="جاري جلب البيانات... ⏳", parse_mode=ParseMode.HTML)
    except TelegramError:
        LOGGER.exception("Unable to send loading message")
        return None


async def _edit_loading_message(
    update: Update,
    loading_message: Message | None,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    """Edit the loading message or fall back to a normal reply."""

    if loading_message is not None:
        try:
            await loading_message.edit_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return
        except BadRequest:
            LOGGER.warning("Loading message could not be edited; falling back to a new reply.")
        except TelegramError:
            LOGGER.exception("Unexpected Telegram failure while editing loading message")

    message = update.effective_message
    if message is not None:
        try:
            await message.reply_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except TelegramError:
            LOGGER.exception("Unable to send fallback loading/result message")


def _field_prompt_text(field: FlowField) -> str:
    return f"{field.prompt}\n\n{SKIP_HINT_TEXT}"


def _parse_user_input(field: FlowField, raw_text: str) -> str | None:
    text = raw_text.strip()
    if not text:
        return None
    if text == ARABIC_SKIP_COMMAND:
        return None

    if field.options:
        for label, value in field.options:
            if text == value or text.lower() == label.lower():
                return value
        return None

    return text


def _should_short_circuit_lines(session: FlowSession) -> bool:
    """Return True once the /lines flow has a meaningful poet or poem query."""

    return bool(session.values.get("poet_id") or session.values.get("poem_id"))


def _should_short_circuit_line(session: FlowSession) -> bool:
    """Return True once the /line flow has a direct line, poem, or poet query."""

    return bool(
        session.values.get("line_id")
        or session.values.get("poem_id")
        or session.values.get("poet_id")
    )


async def _advance_or_complete(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    definition: FlowDefinition,
    session: FlowSession,
) -> int:
    session.field_index += 1
    if session.field_index < len(definition.fields):
        _set_session(context, session)
        current_field = _get_current_field(session, definition)
        await _send_prompt(update, _field_prompt_text(current_field), _build_prompt_keyboard(current_field))
        return FlowState.COLLECTING

    return await _finalize_flow(update, context, definition, session)


async def _complete_now(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    definition: FlowDefinition,
    session: FlowSession,
) -> int:
    """Finalize the conversation immediately after the primary query step."""
    return await _finalize_flow(update, context, definition, session)


async def _finalize_flow(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    definition: FlowDefinition,
    session: FlowSession,
) -> int:
    """Show loading, call the API, then replace the loading state with the final result."""

    loading_message = await _send_loading_message(update)

    try:
        result = await definition.executor(context.bot_data["kather_client"], session.values, 1)
        rendered = definition.renderer(result)
    except (ApiTimeoutError, ApiNetworkError):
        LOGGER.exception("Network failure during flow execution", extra={"flow": definition.name})
        await _edit_loading_message(update, loading_message, ERROR_NETWORK_TEXT)
        _clear_session(context)
        return ConversationHandler.END
    except ApiNotFoundError:
        await _edit_loading_message(update, loading_message, ERROR_NOT_FOUND_TEXT)
        _clear_session(context)
        return ConversationHandler.END
    except (ApiResponseError, ApiError, HikmaError):
        LOGGER.exception("API failure during flow execution", extra={"flow": definition.name})
        await _edit_loading_message(update, loading_message, ERROR_GENERIC_TEXT)
        _clear_session(context)
        return ConversationHandler.END

    _clear_session(context)

    if definition.name == "lines":
        context.user_data[LINES_PAGINATION_KEY] = {"values": dict(session.values), "page": 1}

    await _edit_loading_message(update, loading_message, rendered.text, rendered.keyboard)
    return ConversationHandler.END


async def _send_rendered(update: Update, rendered: RenderedMessage) -> None:
    message = update.effective_message
    if message is None:
        return

    keyboard = rendered.keyboard
    if update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text(text=rendered.text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await message.reply_text(text=rendered.text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def start_flow(update: Update, context: ContextTypes.DEFAULT_TYPE, flow_name: str) -> int:
    """Initialize a conversation and prompt the first field."""

    definition = _get_definition(flow_name)
    session = FlowSession(flow_name=flow_name)
    _set_session(context, session)

    first_field = _get_current_field(session, definition)
    await _send_prompt(update, _field_prompt_text(first_field), _build_prompt_keyboard(first_field))
    return FlowState.COLLECTING


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle free-text input for the active conversation."""

    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    session = _get_session(context)
    if session is None:
        return ConversationHandler.END

    definition = _get_definition(session.flow_name)
    current_field = _get_current_field(session, definition)
    parsed = _parse_user_input(current_field, message.text)

    if parsed is None and message.text.strip() != ARABIC_SKIP_COMMAND:
        await message.reply_text(
            text=f"<b>الرجاء اختيار قيمة صحيحة لحقل {current_field.key}.</b>\n\n{_field_prompt_text(current_field)}",
            parse_mode=ParseMode.HTML,
            reply_markup=_build_prompt_keyboard(current_field),
        )
        return FlowState.COLLECTING

    if parsed is not None:
        session.values[current_field.key] = parsed
    else:
        session.values[current_field.key] = None

    if definition.name == "line" and _should_short_circuit_line(session):
        return await _complete_now(update, context, definition, session)

    if definition.name == "lines" and _should_short_circuit_lines(session):
        return await _complete_now(update, context, definition, session)

    if session.field_index == 0:
        return await _complete_now(update, context, definition, session)

    return await _advance_or_complete(update, context, definition, session)


async def handle_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle inline keyboard choices for the active conversation."""

    query = update.callback_query
    if query is None or query.data is None:
        return ConversationHandler.END

    session = _get_session(context)
    if session is None:
        await query.answer()
        return ConversationHandler.END

    definition = _get_definition(session.flow_name)
    current_field = _get_current_field(session, definition)
    prefix = f"{CallbackData.FLOW_PREFIX}:{CallbackData.CHOICE_PREFIX}:"
    skip_prefix = f"{CallbackData.FLOW_PREFIX}:{CallbackData.SKIP_PREFIX}:"

    if query.data.startswith(skip_prefix):
        try:
            _, _, field_key = query.data.split(":", 2)
        except ValueError:
            await query.answer("بيانات غير صالحة.")
            return FlowState.COLLECTING

        if field_key != current_field.key:
            await query.answer("هذا الاختيار لم يعد مناسباً للخطوة الحالية.")
            return FlowState.COLLECTING

        await query.answer()
        session.values[current_field.key] = None
        return await _advance_or_complete(update, context, definition, session)

    if not query.data.startswith(prefix):
        await query.answer()
        return FlowState.COLLECTING

    try:
        _, _, field_key, value = query.data.split(":", 3)
    except ValueError:
        await query.answer("بيانات غير صالحة.")
        return FlowState.COLLECTING

    if field_key != current_field.key:
        await query.answer("هذا الاختيار لم يعد مناسباً للخطوة الحالية.")
        return FlowState.COLLECTING

    await query.answer()
    session.values[current_field.key] = value

    if definition.name == "line" and _should_short_circuit_line(session):
        return await _complete_now(update, context, definition, session)

    if definition.name == "lines" and _should_short_circuit_lines(session):
        return await _complete_now(update, context, definition, session)

    if session.field_index == 0:
        return await _complete_now(update, context, definition, session)

    return await _advance_or_complete(update, context, definition, session)


async def handle_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip the current field and continue the conversation."""

    session = _get_session(context)
    if session is None:
        return ConversationHandler.END

    definition = _get_definition(session.flow_name)
    current_field = _get_current_field(session, definition)
    session.values[current_field.key] = None
    return await _advance_or_complete(update, context, definition, session)


async def cancel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the active conversation and clear stored state."""

    _clear_session(context)
    message = update.effective_message
    if message is not None:
        await message.reply_text("<b>تم إلغاء العملية.</b>", parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def get_lines_pagination_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any] | None:
    state = context.user_data.get(LINES_PAGINATION_KEY)
    return state if isinstance(state, dict) else None


def set_lines_pagination_state(context: ContextTypes.DEFAULT_TYPE, values: Mapping[str, str | None], page: int) -> None:
    context.user_data[LINES_PAGINATION_KEY] = {"values": dict(values), "page": page}
