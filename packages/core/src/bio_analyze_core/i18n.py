from __future__ import annotations


def extract_i18n_desc(desc: str) -> dict[str, str]:
    """
    Extract bilingual description from a single string.

    Supports two formats:
    1. "zh: 中文描述\nen: English description" (Multi-line with prefixes)
    2. "中文描述 [EN] English description" (Legacy format)

    Args:
        desc (str): The description string to parse.

    Returns:
        Dict[str, str]: A dictionary with keys 'zh' and 'en'.
    """
    if not desc:
        return {"zh": "", "en": ""}

    # Check for prefix format (zh: ... en: ...)
    if "zh:" in desc or "en:" in desc:
        lines = desc.split("\n")
        zh_lines = []
        en_lines = []
        current_lang = None  # 'zh' or 'en'

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("zh:"):
                current_lang = "zh"
                zh_lines.append(stripped[3:].strip())
            elif stripped.startswith("en:"):
                current_lang = "en"
                en_lines.append(stripped[3:].strip())
            elif current_lang == "zh":
                zh_lines.append(stripped)
            elif current_lang == "en":
                en_lines.append(stripped)
            else:
                # If common lines exist before any tag (e.g. initial summary)
                # Add to both if no language context is set yet
                if not current_lang:
                    zh_lines.append(stripped)
                    en_lines.append(stripped)

        zh_text = "\n".join(zh_lines).strip()
        en_text = "\n".join(en_lines).strip()

        # Fallback if one missing
        if zh_text and not en_text:
            en_text = zh_text
        if en_text and not zh_text:
            zh_text = en_text

        if zh_text or en_text:
            return {"zh": zh_text, "en": en_text}

    # Legacy format check or plain text
    parts = desc.split("[EN]")
    zh_desc = parts[0].strip()
    en_desc = parts[1].strip() if len(parts) > 1 else zh_desc

    return {"zh": zh_desc, "en": en_desc}


def get_target_text(text: str, lang: str = "en") -> str:
    """
    Get text for a specific language from a potentially multilingual string.

    Args:
        text (str): The source text (e.g. "zh: ...\nen: ...").
        lang (str): The target language code ('zh' or 'en'). Defaults to 'en'.

    Returns:
        str: The extracted text for the target language.
    """
    if not text:
        return ""

    # Normalize lang
    if lang.startswith("zh"):
        target = "zh"
    else:
        target = "en"

    i18n_dict = extract_i18n_desc(text)
    return i18n_dict.get(target, text)
