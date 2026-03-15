# CLI 国际化 (i18n) 设计方案

本方案旨在让 CLI 工具能够根据用户环境显示对应语言的帮助信息，同时保持代码中的国际化配置能够被元数据生成脚本解析。

## 1. 核心设计原则

*   **单一数据源 (Single Source of Truth)**: 保持现有的 `zh: ...\nen: ...` 格式作为帮助文本的标准写法。这既是代码中的注释/参数，也是元数据生成的来源。
*   **运行时本地化 (Runtime Localization)**: 在 CLI 启动时（执行命令前），动态修改 Typer/Click 的内部对象，根据当前语言环境过滤帮助文本。
*   **共享解析逻辑**: 将文本解析逻辑提取到 `core` 模块，供 CLI 运行时和元数据生成脚本共同使用，确保行为一致。

## 2. 模块架构

### 2.1 核心解析模块 (`packages/core`)
新建 `packages/core/src/bio_analyze_core/i18n.py`：
*   **功能**: 提供通用的文本解析和语言获取功能。
*   **API**:
    *   `parse_i18n_text(text: str) -> dict[str, str]`: 解析 `zh:`/`en:` 格式字符串。
    *   `get_target_text(text: str, lang: str = "en") -> str`: 根据语言代码返回对应文本。

### 2.2 CLI 运行时处理 (`packages/cli`)
新建 `packages/cli/src/bio_analyze_cli/i18n_utils.py`：
*   **功能**: 处理 Typer 应用对象的本地化。
*   **逻辑**:
    *   `detect_language()`: 检测优先级 `BIO_ANALYZE_LANG` > `LANG` > 默认 "en"。
    *   `localize_app(app: typer.Typer)`: 递归遍历 Typer 应用的命令和子命令组。
        *   修改 `CommandInfo.help`。
        *   通过内省（Introspection）遍历命令回调函数的默认参数（`__defaults__`），找到 `OptionInfo` 和 `ArgumentInfo` 对象，修改其 `help` 属性。

### 2.3 入口点集成 (`packages/cli/src/bio_analyze_cli/main.py`)
*   在 `if __name__ == "__main__":` 或 `main()` 函数中，在调用 `app()` 之前执行 `localize_app(app)`。

### 2.4 元数据脚本更新 (`scripts/generate_metadata.py`)
*   移除脚本内硬编码的解析逻辑。
*   引入 `bio_analyze_core.i18n` 进行解析，确保生成的文档与 CLI 行为一致。

## 3. 详细实施步骤

### 步骤 1: 创建 Core i18n 模块
在 `packages/core/src/bio_analyze_core/i18n.py` 中实现解析逻辑。

```python
def extract_i18n_desc(desc: str) -> dict[str, str]:
    # 迁移原脚本中的逻辑
    ...

def get_text_by_lang(desc: str, lang: str = "en") -> str:
    # 调用 extract_i18n_desc 并返回指定语言
    ...
```

### 步骤 2: 实现 CLI 本地化工具
在 `packages/cli/src/bio_analyze_cli/i18n_utils.py` 中实现 Typer 对象修改逻辑。

*   **难点**: Typer 将参数信息存储在函数的默认值中。
*   **解决方案**: 遍历 `app.registered_commands` -> 获取 `callback` -> 访问 `callback.__defaults__` (针对位置/默认参数) 和 `callback.__kwdefaults__` (针对命名参数) -> 找到 `typer.models.OptionInfo` 和 `ArgumentInfo` 实例 -> 原地修改 `help` 字段。

### 步骤 3: 修改 CLI 入口
修改 `packages/cli/src/bio_analyze_cli/main.py`：

```python
from bio_analyze_cli.i18n_utils import localize_app

# ... 定义 app ...

def main():
    localize_app(app)
    app()
```

### 步骤 4: 更新元数据生成脚本
修改 `scripts/generate_metadata.py`，引入 `bio_analyze_core`。

## 4. 验证计划

1.  **单元测试**:
    *   测试 `core.i18n` 解析各种格式字符串的正确性。
    *   测试 `cli.i18n_utils` 是否正确修改了 Typer 对象的帮助信息。
2.  **集成测试**:
    *   设置环境变量 `BIO_ANALYZE_LANG=zh`，运行 `bio-analyze --help`，确认显示中文。
    *   设置环境变量 `BIO_ANALYZE_LANG=en`，运行 `bio-analyze --help`，确认显示英文。
    *   运行 `python scripts/generate_metadata.py`，检查生成的 JSON 文件是否包含双语信息。

## 5. 假设与依赖
*   假设 Typer/Click 的对象在应用启动前是可变的（已验证可行，因为 Typer 在调用时才转换为 Click 对象）。
*   假设所有帮助文本都遵循 `zh: ...\nen: ...` 规范。
