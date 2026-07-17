"""Lines domain service wrappers."""

from __future__ import annotations

from typing import Any

from ..constants import COUNTRY_QUERY_PARAM, ERA_QUERY_PARAM, QUAFIA_QUERY_PARAM, SEA_QUERY_PARAM, TOPIC_QUERY_PARAM
from .client import ChoiceType, KatherApiClient


async def get_lines(
    client: KatherApiClient,
    *,
    poet: str | None = None,
    poem: str | None = None,
    line_type: str | None = None,
    gender: str | None = None,
    era: str | None = None,
    country: str | None = None,
    poem_type: str | None = None,
    topic: str | None = None,
    quafia: str | None = None,
    sea: str | None = None,
    page: int = 1,
    limit: int = 6,
) -> dict[str, Any]:
    """Fetch a paginated lines response matching the supplied filters."""

    return await client.get_lines(
        poet=poet,
        poem=poem,
        line_type=line_type,
        gender=gender,
        era=era,
        country=country,
        poem_type=poem_type,
        topic=topic,
        quafia=quafia,
        sea=sea,
        page=page,
        limit=limit,
    )


async def get_lines_autocomplete(
    client: KatherApiClient,
    *,
    option_name: str,
    option_value: str,
) -> list[ChoiceType]:
    """Fetch lines autocomplete choices for Telegram prompt flows."""

    normalized_option = {
        COUNTRY_QUERY_PARAM: "country",
        ERA_QUERY_PARAM: "era",
        TOPIC_QUERY_PARAM: "topic",
        QUAFIA_QUERY_PARAM: "quafia",
        SEA_QUERY_PARAM: "sea",
        "poem": "poem",
        "poet": "poet",
        "line_id": "line_id",
    }.get(option_name, option_name)
    return await client.get_lines_autocomplete(option_name=normalized_option, option_value=option_value)
