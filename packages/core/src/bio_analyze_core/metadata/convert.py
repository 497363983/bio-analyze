from __future__ import annotations

from typing import Any

from bio_analyze_core.i18n_gettext import Translator


def _bilingual(text: str, translator: Translator) -> dict[str, str]:
    original_language = translator.get_language()
    try:
        translator.set_language("en_US")
        en_text = translator.gettext(text) if text else ""
        if not en_text:
            en_text = text
        translator.set_language("zh_CN")
        zh_text = translator.gettext(text) if text else ""
        if not zh_text:
            zh_text = en_text
        return {"zh": zh_text, "en": en_text}
    finally:
        translator.set_language(original_language)


def schema_to_metadata(schema_entry: dict[str, Any], translator: Translator) -> dict[str, Any]:
    return {
        "name": schema_entry["name"],
        "type": schema_entry["type"],
        "description": _bilingual(schema_entry.get("description", ""), translator),
        "params": [
            {
                "name": param["name"],
                "type": param["type"],
                "required": param["required"],
                "default": param["default"],
                "description": _bilingual(param.get("description", ""), translator),
            }
            for param in schema_entry.get("params", [])
        ],
    }
