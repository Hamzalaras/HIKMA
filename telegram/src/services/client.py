"""Async HTTP client for the Kather API."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, TypeAlias
from urllib.parse import quote_plus, urlencode
import logging

import httpx

from ..constants import (
    API_BASE_URL,
    API_ENDPOINTS,
    API_ROUTES,
    DEFAULT_HTTP_TIMEOUT_SECONDS,
    COUNTRY_QUERY_PARAM,
    ERA_QUERY_PARAM,
    PAGE_SIZE_DEFAULT,
    QUAFIA_QUERY_PARAM,
    SEA_QUERY_PARAM,
    TOPIC_QUERY_PARAM,
)
from ..utils.errors import ApiNetworkError, ApiNotFoundError, ApiResponseError, ApiTimeoutError

JsonType: TypeAlias = dict[str, Any]
JsonListType: TypeAlias = list[dict[str, Any]]
ChoiceType: TypeAlias = dict[str, str]

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class KatherApiClientConfig:
    """Runtime configuration for the Kather API client."""

    base_url: str = API_BASE_URL
    timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS
    default_limit: int = PAGE_SIZE_DEFAULT


class KatherApiClient:
    """High-level async client for the Kather poetry API."""

    def __init__(
        self,
        *,
        config: KatherApiClientConfig | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._config = config or KatherApiClientConfig()
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "KatherApiClient":
        if self._client is None:
            self._client = self._build_client()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator["KatherApiClient"]:
        """Provide a scoped async context manager for temporary usage."""

        async with self as client:
            yield client

    def _build_client(self) -> httpx.AsyncClient:
        timeout = httpx.Timeout(self._config.timeout_seconds)
        return httpx.AsyncClient(base_url=self._config.base_url, timeout=timeout, follow_redirects=True)

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = self._build_client()
        return self._client

    async def _request_json(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> JsonType:
        try:
            LOGGER.debug("Requesting Kather API", extra={"path": path, "params": dict(params or {})})
            response = await self.client.get(path, params=params)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            LOGGER.exception("Kather API request timed out", extra={"path": path})
            raise ApiTimeoutError() from exc
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            LOGGER.warning(
                "Kather API returned an HTTP error",
                extra={"path": path, "status_code": status_code},
            )
            if status_code == httpx.codes.NOT_FOUND:
                raise ApiNotFoundError(f"Resource not found: {path}") from exc
            raise ApiNetworkError(f"HTTP error from API: {status_code}") from exc
        except httpx.HTTPError as exc:
            LOGGER.exception("Kather API transport failure", extra={"path": path})
            raise ApiNetworkError() from exc

        try:
            data = response.json()
        except ValueError as exc:
            LOGGER.exception("Kather API response was not valid JSON", extra={"path": path})
            raise ApiResponseError("API response was not valid JSON.") from exc

        if not isinstance(data, dict):
            raise ApiResponseError("API response payload must be an object.")

        status = data.get("status")
        if status != "success":
            message = data.get("message")
            if isinstance(message, str) and message.strip():
                raise ApiNotFoundError(message)
            raise ApiResponseError("API reported an unexpected status.")

        return data

    @staticmethod
    def _build_query(params: Mapping[str, Any]) -> str:
        filtered = {key: value for key, value in params.items() if value not in (None, "")}
        query = urlencode(filtered, doseq=True)
        return f"?{query}" if query else ""

    @staticmethod
    def _search_query(value: str) -> str:
        return quote_plus(value)

    @staticmethod
    def _is_numeric_identifier(value: str) -> bool:
        return value.isdigit()

    @classmethod
    def _resolve_single_resource_path(
        cls,
        collection: str,
        value: str,
    ) -> str:
        if cls._is_numeric_identifier(value):
            return f"{collection}/{value}"
        return f"{collection}/random?q={cls._search_query(value)}"

    @classmethod
    def _resolve_lines_path(
        cls,
        *,
        value: str,
        limit: int,
        offset: int,
    ) -> str:
        if cls._is_numeric_identifier(value):
            return f"{API_ROUTES['LINES']}?{urlencode({'poemId': value, 'limit': limit, 'offset': offset})}"
        return f"{API_ROUTES['LINES']}/random?q={cls._search_query(value)}&limit={limit}&offset={offset}"

    @staticmethod
    def _ensure_dict(value: Any, *, message: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ApiResponseError(message)
        return value

    @staticmethod
    def _ensure_list_of_dicts(value: Any, *, message: str) -> JsonListType:
        if not isinstance(value, list):
            raise ApiResponseError(message)

        normalized: JsonListType = []
        for item in value:
            if isinstance(item, dict):
                normalized.append(item)
        return normalized

    @staticmethod
    def _choice_from_item(item: Mapping[str, Any]) -> ChoiceType:
        name = item.get("name") or item.get("name_ar") or item.get("name_en") or item.get("content")
        identifier = item.get("id")
        return {"name": str(name or "غير محدد"), "value": str(identifier or "")}

    async def get_poet(
        self,
        *,
        poet_id: str | None = None,
        gender: str | None = None,
        era: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any]:
        if poet_id:
            path = self._resolve_single_resource_path(API_ROUTES['POETS'], poet_id)
            data = await self._request_json(path)
        else:
            query = self._build_query({"gender": gender, ERA_QUERY_PARAM: era, COUNTRY_QUERY_PARAM: country})
            data = await self._request_json(f"{API_ROUTES['POETS']}/random{query}")

        payload = data.get("data")
        if not isinstance(payload, dict):
            raise ApiResponseError("Poet payload was not an object.")
        return payload

    async def get_poet_autocomplete(self, *, option_name: str, option_value: str) -> list[ChoiceType]:
        if option_name == "poet_id":
            path = f"{API_ROUTES['POETS']}?q={self._search_query(option_value)}&limit=25"
        elif option_name == "era":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['ERA']}"
        elif option_name == "country":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['COUNTRY']}"
        else:
            path = f"{API_ROUTES['POETS']}?q={self._search_query(option_value)}&limit=25"

        data = await self._request_json(path)
        payload = self._ensure_list_of_dicts(data.get("data"), message="Poet autocomplete payload must be a list.")
        lowered = option_value.lower()
        choices: list[ChoiceType] = []

        for item in payload:
            lookup_values = [item.get("name_en"), item.get("name_ar"), *(item.get("aliases") or [])]
            if not lowered:
                choices.append({"name": str(item.get("name_ar") or item.get("name") or "غير محدد"), "value": str(item.get("id") or "")})
                continue

            normalized = [str(value).lower() for value in lookup_values if value]
            if any(lowered in value for value in normalized):
                choices.append({"name": str(item.get("name_ar") or item.get("name") or "غير محدد"), "value": str(item.get("id") or "")})

        return choices

    async def get_poem(
        self,
        *,
        poem_id: str | None = None,
        gender: str | None = None,
        era: str | None = None,
        country: str | None = None,
        poem_type: str | None = None,
        topic: str | None = None,
        quafia: str | None = None,
        sea: str | None = None,
    ) -> dict[str, Any]:
        if poem_id:
            path = self._resolve_single_resource_path(API_ROUTES['POEMS'], poem_id)
            data = await self._request_json(path)
        else:
            query = self._build_query(
                {
                    "gender": gender,
                    ERA_QUERY_PARAM: era,
                    COUNTRY_QUERY_PARAM: country,
                    "poemType": poem_type,
                    TOPIC_QUERY_PARAM: topic,
                    QUAFIA_QUERY_PARAM: quafia,
                    SEA_QUERY_PARAM: sea,
                }
            )
            data = await self._request_json(f"{API_ROUTES['POEMS']}/random{query}")

        payload = data.get("data")
        if not isinstance(payload, dict):
            raise ApiResponseError("Poem payload was not an object.")
        return payload

    async def get_poem_autocomplete(self, *, option_name: str, option_value: str) -> list[ChoiceType]:
        if option_name == "era":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['ERA']}"
        elif option_name == "country":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['COUNTRY']}"
        elif option_name == "topic":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['TOPIC']}"
        elif option_name == "quafia":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['QUAFIA']}"
        elif option_name == "sea":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['SEA']}"
        else:
            path = f"{API_ROUTES['POEMS']}?q={self._search_query(option_value)}"

        data = await self._request_json(path)
        payload = self._ensure_list_of_dicts(data.get("data"), message="Poem autocomplete payload must be a list.")
        lowered = option_value.lower()
        choices: list[ChoiceType] = []

        for item in payload:
            lookup_values = [item.get("name"), item.get("name_ar"), item.get("name_en"), *(item.get("aliases") or [])]
            normalized = [str(value).lower() for value in lookup_values if value]
            if not lowered or any(lowered in value for value in normalized):
                choices.append({"name": str(item.get("name") or item.get("name_ar") or "غير محدد"), "value": str(item.get("id") or "")})

        return choices

    async def get_lines(
        self,
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
        limit: int = PAGE_SIZE_DEFAULT,
    ) -> dict[str, Any]:
        offset = max(page - 1, 0) * limit
        if poem:
            if self._is_numeric_identifier(poem):
                query = self._build_query(
                    {
                        "poemId": poem,
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                        "limit": limit,
                        "offset": offset,
                    }
                )
            else:
                query = self._build_query(
                    {
                        "q": self._search_query(poem),
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                        "limit": limit,
                        "offset": offset,
                    }
                )
        elif poet:
            if self._is_numeric_identifier(poet):
                query = self._build_query(
                    {
                        "poetId": poet,
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                        "limit": limit,
                        "offset": offset,
                    }
                )
            else:
                query = self._build_query(
                    {
                        "q": self._search_query(poet),
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                        "limit": limit,
                        "offset": offset,
                    }
                )
        else:
            query = self._build_query(
                {
                    "gender": gender,
                    ERA_QUERY_PARAM: era,
                    COUNTRY_QUERY_PARAM: country,
                    "lineType": line_type,
                    "poemType": poem_type,
                    TOPIC_QUERY_PARAM: topic,
                    QUAFIA_QUERY_PARAM: quafia,
                    SEA_QUERY_PARAM: sea,
                    "limit": limit,
                    "offset": offset,
                }
            )

        data = await self._request_json(f"{API_ROUTES['LINES']}{query}")
        payload = data.get("data")
        if not isinstance(payload, list) or not payload:
            raise ApiNotFoundError("No line records were returned.")
        return data

    async def get_lines_autocomplete(self, *, option_name: str, option_value: str) -> list[ChoiceType]:
        if option_name == "poem":
            path = f"{API_ROUTES['POEMS']}?q={self._search_query(option_value)}"
        elif option_name == "poet":
            path = f"{API_ROUTES['POETS']}?q={self._search_query(option_value)}&limit=25"
        elif option_name == "era":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['ERA']}"
        elif option_name == "country":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['COUNTRY']}"
        elif option_name == "topic":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['TOPIC']}"
        elif option_name == "quafia":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['QUAFIA']}"
        elif option_name == "sea":
            path = f"{API_ROUTES['CATALOG']}{API_ENDPOINTS['CATALOG']['SEA']}"
        else:
            return []

        data = await self._request_json(path)
        payload = self._ensure_list_of_dicts(data.get("data"), message="Lines autocomplete payload must be a list.")
        lowered = option_value.lower()
        choices: list[ChoiceType] = []

        for item in payload:
            lookup_values = [item.get("name"), item.get("name_ar"), item.get("name_en"), *(item.get("aliases") or [])]
            normalized = [str(value).lower() for value in lookup_values if value]
            if not lowered or any(lowered in value for value in normalized):
                choices.append({"name": str(item.get("name") or item.get("name_ar") or "غير محدد"), "value": str(item.get("id") or "")})

        return choices

    async def get_single_line(
        self,
        *,
        line_id: str | None = None,
        poem: str | None = None,
        poet: str | None = None,
        line_type: str | None = None,
        gender: str | None = None,
        era: str | None = None,
        country: str | None = None,
        poem_type: str | None = None,
        topic: str | None = None,
        quafia: str | None = None,
        sea: str | None = None,
    ) -> dict[str, Any]:
        if line_id:
            path = self._resolve_single_resource_path(API_ROUTES['LINES'], line_id)
            data = await self._request_json(path)
        elif poem:
            if self._is_numeric_identifier(poem):
                query = self._build_query(
                    {
                        "poemId": poem,
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                    }
                )
                data = await self._request_json(f"{API_ROUTES['LINES']}/random{query}")
            else:
                query = self._build_query(
                    {
                        "q": self._search_query(poem),
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                    }
                )
                data = await self._request_json(f"{API_ROUTES['LINES']}/random{query}")
        elif poet:
            if self._is_numeric_identifier(poet):
                query = self._build_query(
                    {
                        "poetId": poet,
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                    }
                )
                data = await self._request_json(f"{API_ROUTES['LINES']}/random{query}")
            else:
                query = self._build_query(
                    {
                        "q": self._search_query(poet),
                        "lineType": line_type,
                        "poemType": poem_type,
                        "gender": gender,
                        ERA_QUERY_PARAM: era,
                        COUNTRY_QUERY_PARAM: country,
                        TOPIC_QUERY_PARAM: topic,
                        QUAFIA_QUERY_PARAM: quafia,
                        SEA_QUERY_PARAM: sea,
                    }
                )
                data = await self._request_json(f"{API_ROUTES['LINES']}/random{query}")
        else:
            query = self._build_query(
                {
                    "gender": gender,
                    ERA_QUERY_PARAM: era,
                    COUNTRY_QUERY_PARAM: country,
                    "lineType": line_type,
                    "poemType": poem_type,
                    TOPIC_QUERY_PARAM: topic,
                    QUAFIA_QUERY_PARAM: quafia,
                    SEA_QUERY_PARAM: sea,
                }
            )
            data = await self._request_json(f"{API_ROUTES['LINES']}/random{query}")

        payload = data.get("data")
        if not isinstance(payload, dict):
            raise ApiResponseError("Line payload was not an object.")
        return payload

    async def get_single_line_autocomplete(self, *, option_name: str, option_value: str) -> list[ChoiceType]:
        if option_name == "line_id":
            data = await self._request_json(f"{API_ROUTES['LINES']}?q={self._search_query(option_value)}&limit=25")
            payload = self._ensure_list_of_dicts(data.get("data"), message="Line autocomplete payload must be a list.")
            choices: list[ChoiceType] = []
            for item in payload:
                content = str(item.get("content") or "")
                truncated = content[:92] + "..." if len(content) > 95 else content
                choices.append({"name": truncated or "غير محدد", "value": str(item.get("id") or "")})
            return choices

        return await self.get_lines_autocomplete(option_name=option_name, option_value=option_value)
