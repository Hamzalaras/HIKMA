"""Poet domain service wrappers."""

from __future__ import annotations

from typing import Any

from ..constants import COUNTRY_QUERY_PARAM, ERA_QUERY_PARAM
from .client import KatherApiClient, ChoiceType


async def get_poet(
    client: KatherApiClient,
    *,
    poet_id: str | None = None,
    gender: str | None = None,
    era: str | None = None,
    country: str | None = None,
) -> dict[str, Any]:
    """Fetch a poet record or a random poet that matches the supplied filters."""

    return await client.get_poet(poet_id=poet_id, gender=gender, era=era, country=country)


async def get_poet_autocomplete(
    client: KatherApiClient,
    *,
    option_name: str,
    option_value: str,
) -> list[ChoiceType]:
    """Fetch poet autocomplete choices for Telegram prompt flows."""

    normalized_option = {
        "معرف": "poet_id",
        COUNTRY_QUERY_PARAM: "country",
        ERA_QUERY_PARAM: "era",
    }.get(option_name, option_name)
    return await client.get_poet_autocomplete(option_name=normalized_option, option_value=option_value)
