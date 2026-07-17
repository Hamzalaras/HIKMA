"""User-facing text templates and reusable HTML fragments."""

from __future__ import annotations

from typing import Final

HTML_BOLD_OPEN: Final[str] = "<b>"
HTML_BOLD_CLOSE: Final[str] = "</b>"
HTML_BREAK: Final[str] = "<br>"

ARABIC_SKIP_COMMAND: Final[str] = "/skip"

START_TEXT: Final[str] = (
    "<b>أهلاً بك في Hikma</b>\n"
    "اختر أحد الأوامر للحصول على بيت، أبيات، قصيدة، أو معلومات عن شاعر."
)

SKIP_HINT_TEXT: Final[str] = "يمكنك إرسال <b>/skip</b> لتخطي هذا الحقل."
PROMPT_GENDER_TEXT: Final[str] = "اختر الجنس أو أرسل <b>/skip</b>."
PROMPT_ERA_TEXT: Final[str] = "اختر العصر أو أرسل <b>/skip</b>."
PROMPT_COUNTRY_TEXT: Final[str] = "اختر البلد أو أرسل <b>/skip</b>."
PROMPT_TOPIC_TEXT: Final[str] = "اختر الموضوع أو أرسل <b>/skip</b>."
PROMPT_POEM_ID_TEXT: Final[str] = "أرسل معرف القصيدة أو الاسم الجزئي، أو استخدم <b>/skip</b>."
PROMPT_POET_ID_TEXT: Final[str] = "أرسل معرف الشاعر أو الاسم الجزئي، أو استخدم <b>/skip</b>."
PROMPT_POEM_TEXT: Final[str] = "أرسل اسم القصيدة أو جزءاً منه، أو استخدم <b>/skip</b>."
PROMPT_POET_TEXT: Final[str] = "أرسل اسم الشاعر أو جزءاً منه، أو استخدم <b>/skip</b>."

NO_RESULTS_TEXT: Final[str] = (
    "<b>لم يتم العثور على نتائج.</b>\n"
    "جرّب معايير بحث مختلفة أو استخدم أداة أخرى."
)

ERROR_NETWORK_TEXT: Final[str] = (
    "<b>تعذر الاتصال بالخدمة حالياً.</b>\n"
    "حاول مرة أخرى بعد قليل."
)

ERROR_NOT_FOUND_TEXT: Final[str] = (
    "<b>لم يتم العثور على بيانات مطابقة.</b>\n"
    "يمكنك تعديل المعايير أو تجربة /skip."
)

ERROR_GENERIC_TEXT: Final[str] = (
    "<b>حدث خطأ غير متوقع.</b>\n"
    "تم تسجيل المشكلة داخلياً."
)

HELP_TEXT: Final[str] = (
    "<b>مساعدة Hikma</b>\n"
    "- /line: الحصول على بيت واحد\n"
    "- /lines: الحصول على مجموعة أبيات مع ترقيم\n"
    "- /poem: الحصول على قصيدة\n"
    "- /poet: الحصول على شاعر\n\n"
    "يمكنك استخدام <b>/skip</b> لتخطي أي خطوة اختيارية، كما يمكنك إدخال اسم أو معرف مباشرة في أول خطوة."
)

PAGINATION_LABEL_PREVIOUS: Final[str] = "السابق"
PAGINATION_LABEL_NEXT: Final[str] = "التالي"
