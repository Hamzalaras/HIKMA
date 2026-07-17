"""Domain service layer for the Hikma Telegram bot."""

from .client import KatherApiClient
from .line_service import get_single_line, get_single_line_autocomplete
from .lines_service import get_lines, get_lines_autocomplete
from .poem_service import get_poem, get_poem_autocomplete
from .poet_service import get_poet, get_poet_autocomplete

__all__ = [
    "KatherApiClient",
    "get_lines",
    "get_lines_autocomplete",
    "get_poem",
    "get_poem_autocomplete",
    "get_poet",
    "get_poet_autocomplete",
    "get_single_line",
    "get_single_line_autocomplete",
]
