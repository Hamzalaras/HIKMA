"""Schema-aware HTML formatters for Kather API responses."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Mapping, Sequence

from telegram import InlineKeyboardMarkup

from ..constants import NO_RESULTS_TEXT
from .keyboards import build_lines_pagination_keyboard

MAX_TELEGRAM_MESSAGE_LENGTH: int = 3900
DEFAULT_UNKNOWN: str = "غير محدد"


@dataclass(frozen=True, slots=True)
class RenderedMessage:
    """Container for formatted message text and an optional inline keyboard."""

    text: str
    keyboard: InlineKeyboardMarkup | None = None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _text(value: Any, default: str = DEFAULT_UNKNOWN) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _html(value: Any, default: str = DEFAULT_UNKNOWN) -> str:
    return escape(_text(value, default))


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: max(limit - 3, 0)] + "..."


def _format_field(label: str, value: Any) -> str:
    return f"<b>{escape(label)}:</b> {_html(value)}"


def _translate_gender(value: Any) -> str:
    gender = _text(value)
    if gender.lower() == "female":
        return "أنثى"
    if gender.lower() == "male":
        return "ذكر"
    return gender if gender != DEFAULT_UNKNOWN else DEFAULT_UNKNOWN


def _compact_sections(sections: Sequence[str]) -> str:
    return "\n\n".join(section for section in sections if section.strip())


def _fit_message(text: str) -> str:
    if len(text) <= MAX_TELEGRAM_MESSAGE_LENGTH:
        return text
    return text[: MAX_TELEGRAM_MESSAGE_LENGTH - 3] + "..."


def _render_poem_verses(lines: Sequence[Mapping[str, Any]]) -> str:
    rendered: list[str] = []
    ordered_lines = sorted(lines, key=lambda item: int(item.get("order") or 0))
    for index, line in enumerate(ordered_lines, start=1):
        content = _truncate(_text(line.get("content"), DEFAULT_UNKNOWN), 900)
        rendered.append(f"<b>{index}.</b> {escape(content)}")
    return "\n\n".join(rendered)


def render_poet_message(poet: Mapping[str, Any]) -> RenderedMessage:
    """Render a poet profile payload from the API response."""

    era = _mapping(poet.get("era"))
    country = _mapping(poet.get("country"))
    bio = _truncate(_text(poet.get("bio"), "لا تتوفر نبذة تعريفية."), 1200)

    sections = [
        f"<b>🎭 الشاعر: {_html(poet.get('name_ar') or poet.get('name'))}</b>",
        _format_field("نبذة", bio),
        _format_field("الجنس", _translate_gender(poet.get("gender"))),
        _format_field("البلد", country.get("name_ar") or country.get("name") or poet.get("country")),
        _format_field("العصر", era.get("name_ar") or era.get("name") or poet.get("era")),
        _format_field("عدد القصائد", poet.get("poem_count")),
    ]
    return RenderedMessage(text=_fit_message(_compact_sections(sections)))


def render_poem_message(response: Mapping[str, Any]) -> RenderedMessage:
    """Render a poem response payload that contains poem and lines keys."""

    poem = _mapping(response.get("poem"))
    poet = _mapping(poem.get("poet"))
    era = _mapping(poet.get("era"))
    country = _mapping(poet.get("country"))
    sea = _mapping(poem.get("sea"))
    topic = _mapping(poem.get("topic"))
    quafia = _mapping(poem.get("quafia"))
    poem_type = _mapping(poem.get("type"))
    lines = _sequence_of_mappings(response.get("lines"))

    verses = _render_poem_verses(lines) if lines else _text(poem.get("content"), "")
    if verses:
        verses = _truncate(verses, 1800)

    sections = [
        f"<b>📖 القصيدة: {_html(poem.get('name'))}</b>",
        _format_field("الشاعر", poet.get("name_ar") or poet.get("name")),
        _format_field("الجنس", _translate_gender(poet.get("gender"))),
        _format_field("البلد", country.get("name_ar") or country.get("name") or poet.get("country")),
        _format_field("العصر", era.get("name_ar") or era.get("name") or poet.get("era")),
        _format_field("البحر", sea.get("name_ar") or sea.get("name") or poem.get("sea")),
        _format_field("الموضوع", topic.get("name_ar") or topic.get("name") or poem.get("topic")),
        _format_field("القافية", quafia.get("name_ar") or quafia.get("name") or poem.get("quafia")),
        _format_field("نوع القصيدة", poem_type.get("name_ar") or poem_type.get("name") or poem.get("type")),
        verses,
    ]
    return RenderedMessage(text=_fit_message(_compact_sections(sections)))


def render_single_line_message(line: Mapping[str, Any]) -> RenderedMessage:
    """Render a single line with metadata from the nested poem payload."""

    poem = _mapping(line.get("poem"))
    poet = _mapping(poem.get("poet"))
    era = _mapping(poet.get("era"))
    country = _mapping(poet.get("country"))
    sea = _mapping(poem.get("sea"))
    topic = _mapping(poem.get("topic"))
    quafia = _mapping(poem.get("quafia"))
    poem_type = _mapping(poem.get("type"))

    sections = [
        f"<b>📜 البيت:</b> {_html(line.get('content'))}",
        _format_field("الشاعر", poet.get("name_ar") or poet.get("name")),
        _format_field("القصيدة", poem.get("name")),
        _format_field("الجنس", _translate_gender(poet.get("gender"))),
        _format_field("البلد", country.get("name_ar") or country.get("name") or poet.get("country")),
        _format_field("العصر", era.get("name_ar") or era.get("name") or poet.get("era")),
        _format_field("البحر", sea.get("name_ar") or sea.get("name") or poem.get("sea")),
        _format_field("الموضوع", topic.get("name_ar") or topic.get("name") or poem.get("topic")),
        _format_field("القافية", quafia.get("name_ar") or quafia.get("name") or poem.get("quafia")),
        _format_field("نوع القصيدة", poem_type.get("name_ar") or poem_type.get("name") or poem.get("type")),
    ]
    return RenderedMessage(text=_fit_message(_compact_sections(sections)))


def render_lines_message(response: Mapping[str, Any]) -> RenderedMessage:
    """Render a paginated lines response with inline navigation controls."""

    data = _sequence_of_mappings(response.get("data"))
    poem = _mapping(response.get("poem"))
    poet = _mapping(response.get("poet"))
    pagination = _mapping(response.get("pagination"))

    sections = ["<b>📜 الأبيات</b>"]
    if poem:
        poet_name = _mapping(poem.get("poet")).get("name_ar") if isinstance(poem.get("poet"), Mapping) else None
        sections.append(_format_field("القصيدة", poem.get("name")))
        sections.append(_format_field("الشاعر", poet_name or poem.get("poet")))
    elif poet:
        era = _mapping(poet.get("era"))
        sections.append(_format_field("الشاعر", poet.get("name_ar") or poet.get("name")))
        sections.append(_format_field("العصر", era.get("name_ar") or era.get("name") or poet.get("era")))

    lines_block = _render_poem_verses(data[:12]) if data else NO_RESULTS_TEXT
    sections.append(lines_block)

    page = int(pagination.get("page") or 1)
    total_pages = int(pagination.get("total_pages") or 1)
    total_items = pagination.get("total_items") or pagination.get("total")
    footer_parts = [f"الصفحة {page} من {total_pages}"]
    if total_items is not None:
        footer_parts.append(f"إجمالي النتائج: {total_items}")
    sections.append("<i>" + escape(" • ".join(footer_parts)) + "</i>")

    keyboard = build_lines_pagination_keyboard(page, total_pages)
    return RenderedMessage(text=_fit_message(_compact_sections(sections)), keyboard=keyboard)
