"""Callback data values used by inline keyboards."""

from __future__ import annotations

from typing import Final


class CallbackData:
    """Namespace for callback data prefixes and values."""

    FLOW_PREFIX: Final[str] = "flow"
    CHOICE_PREFIX: Final[str] = "choice"
    SKIP_PREFIX: Final[str] = "skip"
    LINES_PREVIOUS: Final[str] = "lines:prev"
    LINES_NEXT: Final[str] = "lines:next"
