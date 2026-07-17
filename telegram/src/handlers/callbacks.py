"""Callback query handlers for inline keyboard pagination."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..constants import CallbackData, ERROR_NETWORK_TEXT, ERROR_NOT_FOUND_TEXT, ERROR_GENERIC_TEXT, PAGE_SIZE_DEFAULT
from ..services.client import KatherApiClient
from ..utils.errors import ApiError, ApiNetworkError, ApiNotFoundError, ApiResponseError, ApiTimeoutError, HikmaError
from ..utils.keyboards import build_lines_pagination_keyboard
from ..utils.formatters import render_lines_message
from .flow import get_lines_pagination_state, set_lines_pagination_state

LOGGER = logging.getLogger(__name__)


async def handle_lines_pagination(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Render a new /lines page based on the stored query context."""

    query = update.callback_query
    if query is None or query.data is None:
        return

    state = get_lines_pagination_state(context)
    if state is None:
        await query.answer("لا توجد حالة ترقيم نشطة.")
        return

    direction = 0
    if query.data == CallbackData.LINES_PREVIOUS:
        direction = -1
    elif query.data == CallbackData.LINES_NEXT:
        direction = 1
    else:
        return

    await query.answer()

    values = state.get("values", {})
    current_page = int(state.get("page") or 1)
    next_page = max(current_page + direction, 1)
    client: KatherApiClient = context.bot_data["kather_client"]

    try:
        response = await client.get_lines(
            poet=values.get("poet_id"),
            poem=values.get("poem_id"),
            line_type=values.get("line_type"),
            gender=values.get("gender"),
            era=values.get("era"),
            country=values.get("country"),
            poem_type=values.get("poem_type"),
            topic=values.get("topic"),
            quafia=values.get("quafia"),
            sea=values.get("sea"),
            page=next_page,
            limit=PAGE_SIZE_DEFAULT,
        )
    except (ApiTimeoutError, ApiNetworkError):
        await query.edit_message_text(text=ERROR_NETWORK_TEXT, parse_mode=ParseMode.HTML)
        LOGGER.exception("Network failure during lines pagination")
        return
    except ApiNotFoundError:
        await query.edit_message_text(text=ERROR_NOT_FOUND_TEXT, parse_mode=ParseMode.HTML)
        return
    except (ApiResponseError, ApiError, HikmaError):
        await query.edit_message_text(text=ERROR_GENERIC_TEXT, parse_mode=ParseMode.HTML)
        LOGGER.exception("API failure during lines pagination")
        return

    rendered = render_lines_message(response)
    pagination = response.get("pagination") if isinstance(response.get("pagination"), dict) else {}
    page = int(pagination.get("page") or next_page)
    total_pages = int(pagination.get("total_pages") or page)
    keyboard = rendered.keyboard or build_lines_pagination_keyboard(page, total_pages)

    await query.edit_message_text(text=rendered.text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    set_lines_pagination_state(context, values, page)
