"""Conversation definitions for the four supported Telegram commands."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..constants import GENDER_OPTIONS, LINE_TYPE_OPTIONS, PAGE_SIZE_DEFAULT, POEM_TYPE_OPTIONS, PROMPT_COUNTRY_TEXT, PROMPT_ERA_TEXT, PROMPT_POEM_ID_TEXT, PROMPT_POET_ID_TEXT, PROMPT_TOPIC_TEXT
from ..services.client import KatherApiClient
from ..services.line_service import get_single_line as service_get_single_line
from ..services.lines_service import get_lines as service_get_lines
from ..services.poem_service import get_poem as service_get_poem
from ..services.poet_service import get_poet as service_get_poet
from ..utils.formatters import RenderedMessage, render_lines_message, render_poem_message, render_poet_message, render_single_line_message
from .states import FlowDefinition, FlowField

def _choice_items(options: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple((label, value) for value, label in options.items())


async def _execute_poet(client: KatherApiClient, values: Mapping[str, str], page: int = 1) -> dict[str, Any]:
    return await service_get_poet(
        client,
        poet_id=values.get("poet_id"),
        gender=values.get("gender"),
        era=values.get("era"),
        country=values.get("country"),
    )


async def _execute_poem(client: KatherApiClient, values: Mapping[str, str], page: int = 1) -> dict[str, Any]:
    return await service_get_poem(
        client,
        poem_id=values.get("poem_id"),
        gender=values.get("gender"),
        era=values.get("era"),
        country=values.get("country"),
        poem_type=values.get("poem_type"),
        topic=values.get("topic"),
        quafia=values.get("quafia"),
        sea=values.get("sea"),
    )


async def _execute_line(client: KatherApiClient, values: Mapping[str, str], page: int = 1) -> dict[str, Any]:
    return await service_get_single_line(
        client,
        line_id=values.get("line_id"),
        poem=values.get("poem_id"),
        poet=values.get("poet_id"),
        line_type=values.get("line_type"),
        gender=values.get("gender"),
        era=values.get("era"),
        country=values.get("country"),
        poem_type=values.get("poem_type"),
        topic=values.get("topic"),
        quafia=values.get("quafia"),
        sea=values.get("sea"),
    )


async def _execute_lines(client: KatherApiClient, values: Mapping[str, str], page: int = 1) -> dict[str, Any]:
    return await service_get_lines(
        client,
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
        page=page,
        limit=PAGE_SIZE_DEFAULT,
    )


FLOW_DEFINITIONS: dict[str, FlowDefinition] = {
    "poet": FlowDefinition(
        name="poet",
        fields=(
            FlowField(key="poet_id", prompt=PROMPT_POET_ID_TEXT),
            FlowField(key="gender", prompt="اختر الجنس أو أرسل /skip.", options=_choice_items(GENDER_OPTIONS)),
            FlowField(key="era", prompt=PROMPT_ERA_TEXT),
            FlowField(key="country", prompt=PROMPT_COUNTRY_TEXT),
        ),
        executor=_execute_poet,
        renderer=render_poet_message,
    ),
    "poem": FlowDefinition(
        name="poem",
        fields=(
            FlowField(key="poem_id", prompt=PROMPT_POEM_ID_TEXT),
            FlowField(key="gender", prompt="اختر الجنس أو أرسل /skip.", options=_choice_items(GENDER_OPTIONS)),
            FlowField(key="era", prompt=PROMPT_ERA_TEXT),
            FlowField(key="country", prompt=PROMPT_COUNTRY_TEXT),
            FlowField(key="poem_type", prompt="اختر نوع القصيدة أو أرسل /skip.", options=_choice_items(POEM_TYPE_OPTIONS)),
            FlowField(key="topic", prompt=PROMPT_TOPIC_TEXT),
            FlowField(key="quafia", prompt="اختر القافية أو أرسل /skip."),
            FlowField(key="sea", prompt="اختر البحر أو أرسل /skip."),
        ),
        executor=_execute_poem,
        renderer=render_poem_message,
    ),
    "line": FlowDefinition(
        name="line",
        fields=(
            FlowField(key="line_id", prompt="أرسل معرف البيت أو الاسم الجزئي، أو استخدم /skip."),
            FlowField(key="poem_id", prompt=PROMPT_POEM_ID_TEXT),
            FlowField(key="poet_id", prompt=PROMPT_POET_ID_TEXT),
            FlowField(key="line_type", prompt="اختر نوع البيت أو أرسل /skip.", options=tuple((label, value) for value, label in LINE_TYPE_OPTIONS.items())),
            FlowField(key="gender", prompt="اختر الجنس أو أرسل /skip.", options=_choice_items(GENDER_OPTIONS)),
            FlowField(key="era", prompt=PROMPT_ERA_TEXT),
            FlowField(key="country", prompt=PROMPT_COUNTRY_TEXT),
            FlowField(key="poem_type", prompt="اختر نوع القصيدة أو أرسل /skip.", options=_choice_items(POEM_TYPE_OPTIONS)),
            FlowField(key="topic", prompt=PROMPT_TOPIC_TEXT),
            FlowField(key="quafia", prompt="اختر القافية أو أرسل /skip."),
            FlowField(key="sea", prompt="اختر البحر أو أرسل /skip."),
        ),
        executor=_execute_line,
        renderer=render_single_line_message,
    ),
    "lines": FlowDefinition(
        name="lines",
        fields=(
            FlowField(key="poet_id", prompt=PROMPT_POET_ID_TEXT),
            FlowField(key="poem_id", prompt=PROMPT_POEM_ID_TEXT),
            FlowField(key="line_type", prompt="اختر نوع البيت أو أرسل /skip.", options=tuple((label, value) for value, label in LINE_TYPE_OPTIONS.items())),
            FlowField(key="gender", prompt="اختر الجنس أو أرسل /skip.", options=_choice_items(GENDER_OPTIONS)),
            FlowField(key="era", prompt=PROMPT_ERA_TEXT),
            FlowField(key="country", prompt=PROMPT_COUNTRY_TEXT),
            FlowField(key="poem_type", prompt="اختر نوع القصيدة أو أرسل /skip.", options=_choice_items(POEM_TYPE_OPTIONS)),
            FlowField(key="topic", prompt=PROMPT_TOPIC_TEXT),
            FlowField(key="quafia", prompt="اختر القافية أو أرسل /skip."),
            FlowField(key="sea", prompt="اختر البحر أو أرسل /skip."),
        ),
        executor=_execute_lines,
        renderer=render_lines_message,
    ),
}
