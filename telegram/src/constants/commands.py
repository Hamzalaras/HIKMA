"""Command names and human-facing command labels."""

from __future__ import annotations

from typing import Final

COMMAND_NAMES: Final[dict[str, str]] = {
    "START": "start",
    "HELP": "help",
    "LINE": "line",
    "LINES": "lines",
    "POEM": "poem",
    "POET": "poet",
    "SKIP": "skip",
}

USER_COMMAND_LABELS: Final[dict[str, str]] = {
    "LINE": "بيت",
    "LINES": "أبيات",
    "POEM": "قصيدة",
    "POET": "شاعر",
    "SKIP": "تخطي",
}

COMMAND_DESCRIPTIONS: Final[dict[str, str]] = {
    "LINE": "Fetch a single poetic line.",
    "LINES": "Fetch a paginated list of poetic lines.",
    "POEM": "Fetch a poem.",
    "POET": "Fetch poet details.",
    "SKIP": "Skip the current conversation step.",
}
