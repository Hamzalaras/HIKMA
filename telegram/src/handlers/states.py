"""Conversation state and session models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from ..services.client import KatherApiClient
from ..utils.messages import RenderedMessage


class FlowState(IntEnum):
    """Single active collection state for the search conversations."""

    COLLECTING = 0


@dataclass(slots=True)
class FlowSession:
    """Per-user conversation state stored in ``context.user_data``."""

    flow_name: str
    values: dict[str, str | None] = field(default_factory=dict)
    field_index: int = 0
    awaiting_selection: bool = False


@dataclass(frozen=True, slots=True)
class FlowField:
    """One prompted search field in a conversation."""

    key: str
    prompt: str
    options: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class FlowDefinition:
    """Metadata that binds a prompt flow to its executor and renderer."""

    name: str
    fields: tuple[FlowField, ...]
    executor: Callable[[KatherApiClient, Mapping[str, str | None], int], Awaitable[dict[str, Any]]]
    renderer: Callable[[Mapping[str, Any]], RenderedMessage]
