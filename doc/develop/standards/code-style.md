# Code Style

To ensure code quality and maintainability, this project follows strict coding standards.

## 1. Python Style

We use [Ruff](https://docs.astral.sh/ruff/) for comprehensive code linting and formatting.

### Core Rules

- **Line Length**: 120 characters.
- **Quote Style**: Double quotes `"`.
- **Import Sorting**: Automatic sorting (isort).
- **Type Hints**: All public functions and class methods must include type hints.

### Example

```python
from pathlib import Path
from typing import List, Optional

def process_files(
    input_files: List[Path],
    output_dir: Path,
    verbose: bool = False
) -> None:
    """
    Process input file list.
    
    Args:
        input_files: List of input file paths
        output_dir: Output directory
        verbose: Whether to print verbose logs
    """
    ...
```

## 2. Comments and Docstrings

All public modules, classes, and functions must include docstrings.

### Documentation Standard

We adopt the **Google Style** docstring format. This format is clear, readable, and can be correctly parsed by our documentation generation tools.

#### Function/Method Docstrings

Must include `Args`, `Returns`, and `Raises` sections (if applicable). Parameter types and optional status should be indicated in parentheses after the parameter name.

```python
def calculate_metrics(data: pd.DataFrame, threshold: float = 0.05) -> dict:
    """
    Calculate key statistics.

    Detailed description can go here, explaining the specific logic, algorithm source, or notes.
    Supports multi-line descriptions.

    Args:
        data (pd.DataFrame): Input dataframe, must contain 'pvalue' column.
        threshold (float, optional): Significance threshold. Defaults to 0.05.

    Returns:
        dict: Dictionary containing statistical results, e.g., {'significant_count': 10}.

    Raises:
        ValueError: Raised when required columns are missing in input data.
    """
    pass
```

#### Class Docstrings

Must describe the purpose of the class and explain initialization parameters.

```python
class VolcanoPlot:
    """
    Volcano Plotting Class.

    Used for visualizing differential expression analysis results, showing relationship between Fold Change and P-value.

    Attributes:
        theme (str): Plot theme name.
    """

    def __init__(self, theme: str = "nature"):
        """
        Initialize plotter.

        Args:
            theme (str, optional): Theme name, defaults to 'nature'.
        """
        self.theme = theme
```

## 3. Internationalization (i18n)

Since our project requires automatic generation of multi-language documentation, we introduced specific markers in code comments (Docstrings) to support multi-language descriptions.

### Formatting Standards

Use `zh:` and `en:` markers in docstrings to distinguish descriptions in different languages. Default unmarked text will be treated as English (or as a generic description).

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

### Parameter Description i18n

For the parameter (Args) section descriptions, multi-language markers are also supported. Our documentation generation script automatically parses these markers and displays Chinese and English descriptions separately in the generated API documentation.

```python
    Args:
        input_dir (Path): 
            Input data directory containing raw FastQ files.
        threads (int, optional):
            Number of parallel threads. Defaults to 4.
```

## 4. Git Commit Standards


This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>
```

### Common Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Examples

- `feat(plot): add support for volcano plot`
- `fix(rna-seq): fix salmon quantization error`
- `docs: update installation guide`

## 5. Automated Checks

When committing code, `pre-commit` automatically runs the following checks:

1. **Ruff Format**: Format code.
2. **Ruff Lint**: Check code style and potential errors.
3. **Commitizen**: Check commit message format.

You can manually run checks:

```bash
# Check all files
pre-commit run --all-files
```
