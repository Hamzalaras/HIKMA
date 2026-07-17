"""Conversation options, filters, and pagination defaults."""

from __future__ import annotations

from typing import Final

PAGE_SIZE_DEFAULT: Final[int] = 6

GENDER_OPTIONS: Final[dict[str, str]] = {
    "male": "ذكر",
    "female": "أنثى",
}

POEM_TYPE_OPTIONS: Final[dict[str, str]] = {
    "1": "عمودية",
    "2": "نثرية",
    "3": "تفعيلة",
    "4": "مترجمة",
}

LINE_TYPE_OPTIONS: Final[dict[str, str]] = {
    "0": "فارغ",
    "1": "صدر",
    "2": "عجز",
    "3": "حر",
}

ERA_QUERY_PARAM: Final[str] = "era"
COUNTRY_QUERY_PARAM: Final[str] = "country"
TOPIC_QUERY_PARAM: Final[str] = "topic"
QUAFIA_QUERY_PARAM: Final[str] = "quafia"
SEA_QUERY_PARAM: Final[str] = "sea"
