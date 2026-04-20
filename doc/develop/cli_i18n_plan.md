# CLI 国际化 (i18n) 设计方案

本文档保留为历史方案说明，但当前实现已经不再依赖 `zh: ... / en: ...` 双语字符串。

## 当前结论

- CLI 帮助文本以英文 `msgid` 作为唯一源码文本。
- 运行时翻译通过 gettext catalog 完成。
- 模块级翻译文件位于 `locale/<lang>/LC_MESSAGES/messages.po` 与 `messages.mo`。
- 元数据生成直接读取英文源码文本，再通过 translator 输出 `zh/en` 结果。

## 当前实现位置

- Core translator: `packages/core/src/bio_analyze_core/i18n_gettext.py`
- Translation wrapper: `packages/core/src/bio_analyze_core/i18n.py`
- CLI localization: `packages/core/src/bio_analyze_core/cli_i18n.py`
- Metadata schema: `packages/core/src/bio_analyze_core/metadata/schema.py`
- Metadata generation: `scripts/generate_metadata.py`

## 当前规则

- 不再在代码中写 `zh: ...` / `en: ...` 双语 help 字符串。
- 新增 help、prompt、docstring 时直接写英文源码文本。
- 中文简体和英文输出统一通过 locale catalog 维护。
