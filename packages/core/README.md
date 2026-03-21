# bio-analyze-core

[![PyPI Version](https://img.shields.io/pypi/v/bio-analyze-core?label=PyPI&include_prereleases&sort=semver&logo=python)](https://pypi.org/project/bio-analyze-core/)

Shared core utilities for the toolbox: provides reusable capabilities (configuration, logging, I/O, external command execution, etc.) for various analysis modules and the CLI.

## 📦 Core Functional Modules

### 1. Logging Management

Provides a unified logging initialization and management mechanism based on `loguru`.

#### Python API

```python
from bio_analyze_core.logging import get_logger, setup_logging

# 1. Unified initialization at the application entry point
# Idempotent design: multiple calls only update the level without breaking existing sinks
setup_logging(level="INFO")

# 2. Get a module-specific logger
# Automatically binds extra["name"] = "my_module"
logger = get_logger("my_module")
logger.info("This is a log message")

# 3. Independent file logging
# Supports setting an independent log file for a specific module
file_logger = get_logger("my_task", log_path="./logs/task.log")
file_logger.info("This goes to file AND console")
```

**`get_logger` parameters:**
- `name` (str): Logger name.
- `log_path` (str | Path, optional): If provided, logs will also be written to this file.
- `level` (str): Log level for the file (default "INFO").

### 2. Pipeline Framework

Provides a Node-based stream processing framework supporting context sharing and state persistence.

#### Python API

```python
from bio_analyze_core.pipeline import Pipeline, Node, Context, Progress

class MyNode(Node):
    def run(self, context: Context, progress: Progress, logger):
        logger.info(f"Processing {context.data}")
        progress.update(message="Working...", percentage=50)
        context.result = "done"

# Create a pipeline
pipeline = Pipeline("my_pipeline", state_file="pipeline_state.json")
pipeline.context.data = "input_data"

# Add nodes
pipeline.add_node(MyNode("step1"))

# Run the pipeline
pipeline.run()
```

### 3. Subprocess Management

Wraps `subprocess.run` to provide safer external command execution and output capturing.

#### Python API

```python
from bio_analyze_core.subprocess import run, CalledProcessError

try:
    result = run(
        ["ls", "-la"],
        cwd="./",
        check=True,          # Raises exception on non-zero exit code
        capture_output=True  # Captures stdout/stderr
    )
    print(result.stdout)
except CalledProcessError as e:
    print(f"Command failed: {e.stderr}")
```

### 4. Configuration Management

Supports loading configurations from JSON/YAML and provides deep merge utilities.

#### Python API

```python
from bio_analyze_core.utils import load_config

# Automatically recognizes .json or .yaml
config = load_config("config.yaml")
print(config["input_dir"])
```
