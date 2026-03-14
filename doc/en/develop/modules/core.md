# bio-analyze-core (Developer Guide)

Toolkit common module: provides reusable capabilities for various analysis modules and CLI (configuration, logging, IO, running external commands, etc.).

## 📦 Core Functional Modules

### 1. Logging

Provides a unified log initialization and management mechanism based on `loguru`.

#### Python API

```python
from bio_analyze_core.logging import get_logger, setup_logging

# 1. Unified initialization at application entry
# Idempotent design: multiple calls only update the level and do not destroy existing Sinks
setup_logging(level="INFO")

# 2. Get module Logger
# Automatically binds extra["name"] = "my_module"
logger = get_logger("my_module")
logger.info("This is a log message")

# 3. Independent file log
# Supports setting independent log files for specific modules
file_logger = get_logger("my_task", log_path="./logs/task.log")
file_logger.info("This goes to file AND console")
```

**`get_logger` Parameters:**
- `name` (str): Logger name.
- `log_path` (str | Path, optional): If provided, logs will also be written to this file.
- `level` (str): File log level (default "INFO").

### 2. Pipeline Framework

Provides a Node-based streaming processing framework supporting context sharing and state persistence.

#### Python API

```python
from bio_analyze_core.pipeline import Pipeline, Node, Context, Progress

class MyNode(Node):
    def run(self, context: Context, progress: Progress, logger):
        logger.info(f"Processing {context.data}")
        progress.update(message="Working...", percentage=50)
        context.result = "done"

# Create pipeline
pipeline = Pipeline("my_pipeline", state_file="pipeline_state.json")
pipeline.context.data = "input_data"

# Add nodes
pipeline.add_node(MyNode("step1"))

# Run
pipeline.run()
```

### 3. Subprocess Management

Encapsulates `subprocess.run`, providing safer external command execution and output capture.

#### Python API

```python
from bio_analyze_core.subprocess import run, CalledProcessError

try:
    result = run(
        ["ls", "-la"],
        cwd="./",
        check=True,          # Raise exception on non-zero exit code
        capture_output=True  # Capture stdout/stderr
    )
    print(result.stdout)
except CalledProcessError as e:
    print(f"Command failed: {e.stderr}")
```

### 4. Configuration Management

Supports loading configuration from JSON/YAML and provides deep merge tools.

#### Python API

```python
from bio_analyze_core.utils import load_config

# Automatically identify .json or .yaml
config = load_config("config.yaml")
print(config["input_dir"])
```
