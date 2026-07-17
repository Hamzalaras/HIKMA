"""API endpoints and transport defaults for the Hikma bot."""

from __future__ import annotations

from typing import Final

API_BASE_URL: Final[str] = "https://kather.onrender.com"
DEFAULT_HTTP_TIMEOUT_SECONDS: Final[float] = 15.0

API_ROUTES: Final[dict[str, str]] = {
    "POETS": f"{API_BASE_URL}/poets",
    "POEMS": f"{API_BASE_URL}/poems",
    "LINES": f"{API_BASE_URL}/lines",
    "CATALOG": f"{API_BASE_URL}/catalog",
}

API_ENDPOINTS: Final[dict[str, dict[str, str]]] = {
    "CATALOG": {
        "ERA": "/eras",
        "COUNTRY": "/countries",
        "TOPIC": "/topics",
        "QUAFIA": "/quawafi",
        "SEA": "/seas",
    }
}
