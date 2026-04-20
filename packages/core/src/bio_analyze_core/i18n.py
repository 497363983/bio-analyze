from __future__ import annotations

from .i18n_gettext import get_current_translator


def _(text: str, *, context: str | None = None, count: int | None = None, plural: str | None = None) -> str:
    """
    Translate text with the current translator.
    """
    translator = get_current_translator()
    if translator is None:
        if count is not None and plural is not None and count != 1:
            return plural
        return text

    if count is not None and plural is not None:
        return translator.ngettext(text, plural, count)
    if context is not None:
        return translator.pgettext(context, text)
    return translator.gettext(text)
