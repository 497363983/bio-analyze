# 代码规范

为保证代码质量和可维护性，本项目遵循严格的代码规范。

## 1. Python 代码风格

我们使用 [Ruff](https://docs.astral.sh/ruff/) 进行全方位的代码检查和格式化。

### 核心规则

- **行长限制**：120 字符。
- **引用风格**：双引号 `"`。
- **导入排序**：自动排序（isort）。
- **类型注解**：必须为所有公开函数和类方法添加类型注解（Type Hints）。

### 示例

```python
from pathlib import Path
from typing import List, Optional

def process_files(
    input_files: List[Path],
    output_dir: Path,
    verbose: bool = False
) -> None:
    """
    处理输入文件列表。
  
    Args:
        input_files: 输入文件路径列表
        output_dir: 输出目录
        verbose: 是否打印详细日志
    """
    ...
```

## 2. 注释与文档字符串 (Docstrings)

所有公开的模块、类、函数必须包含文档字符串。

### 风格标准

我们采用 **Google Style** 的文档字符串格式。这种格式清晰易读，且能被我们的文档生成工具正确解析。

#### 函数/方法注释

必须包含 `Args` (参数)、`Returns` (返回值) 和 `Raises` (抛出异常) 部分（如果适用）。参数名后应在括号中注明参数类型和是否可选。

```python
def calculate_metrics(data: pd.DataFrame, threshold: float = 0.05) -> dict:
    """
    计算关键统计指标。

    详细描述可以在这里展开，解释函数的具体逻辑、算法来源或注意事项。
    支持多行描述。

    Args:
        data (pd.DataFrame): 输入的数据框，必须包含 'pvalue' 列。
        threshold (float, optional): 显著性阈值. 默认为 0.05.

    Returns:
        dict: 包含统计结果的字典，例如 {'significant_count': 10}.

    Raises:
        ValueError: 当输入数据缺失必要列时抛出。
    """
    pass
```

#### 类注释

必须描述类的用途，并说明初始化参数。

```python
class VolcanoPlot:
    """
    火山图绘制类。

    用于可视化差异表达分析结果，展示 Fold Change 与 P-value 的关系。

    Attributes:
        theme (str): 绘图主题名称。
    """

    def __init__(self, theme: str = "nature"):
        """
        初始化绘图器。

        Args:
            theme (str, optional): 主题名称，默认为 'nature'。
        """
        self.theme = theme
```

## 3. 国际化 (i18n)

由于我们的项目需要支持多语言文档自动生成，我们在代码注释（Docstrings）中引入了特定的标记来支持多语言描述。

### 格式规范

在 docstring 中使用 `zh:` 和 `en:` 标记来区分不同语言的描述。默认未标记的文本将被视为英文（或作为通用描述）。

```python
def run_pipeline(config_path: str):
    """
    Run the analysis pipeline.
  
    Run the analysis pipeline. Read the config file and execute tasks sequentially.
  
    Args:
        config_path (str):
            Path to configuration file (.json/.yaml)
    """
    pass
```

### 参数描述的国际化

对于参数（Args）部分的描述，同样支持多语言标记。我们的文档生成脚本会自动解析这些标记，并在生成的 API 文档中分别展示中文和英文描述。

```python
    Args:
        input_dir (Path): 
            Input data directory containing raw FastQ files.
        threads (int, optional):
            Number of parallel threads. Defaults to 4.
```

## 4. Git 提交规范

本项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 格式

```
<type>(<scope>): <subject>
```

### 常用 Type

- `feat`: 新功能 (feature)
- `fix`:虽然修复 (bug fix)
- `docs`: 文档变更
- `style`: 代码格式 (不影响代码运行的变动)
- `refactor`: 重构 (既不是新增功能也不是修改 bug 的代码变动)
- `perf`: 性能优化
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动

### 示例

- `feat(plot): add support for volcano plot`
- `fix(rna-seq): fix salmon quantization error`
- `docs: update installation guide`

## 5. 自动化检查

在提交代码时，`pre-commit` 会自动运行以下检查：

1. **Ruff Format**: 格式化代码。
2. **Ruff Lint**: 检查代码风格和潜在错误。
3. **Commitizen**: 检查提交信息格式。

您可以手动运行检查：

```bash
# 检查所有文件
pre-commit run --all-files
```
