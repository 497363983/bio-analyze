# bio-analyze-core

工具箱公共模块：为各个分析模块与 CLI 提供复用能力（配置、日志、IO、运行外部命令等）。

## 📦 核心功能模块

### 1. 日志管理 (Logging)

提供统一的日志初始化与管理机制，基于 `loguru`。

#### Python API

```python
from bio_analyze_core.logging import get_logger, setup_logging

# 1. 应用入口统一初始化
# 幂等设计：多次调用仅更新级别，不会破坏已存在的 Sink
setup_logging(level="INFO")

# 2. 获取模块 Logger
# 自动绑定 extra["name"] = "my_module"
logger = get_logger("my_module")
logger.info("This is a log message")

# 3. 独立文件日志
# 支持为特定模块设置独立日志文件
file_logger = get_logger("my_task", log_path="./logs/task.log")
file_logger.info("This goes to file AND console")
```

**`get_logger` 参数:**
- `name` (str): Logger 名称。
- `log_path` (str | Path, optional): 如果提供，日志也将写入此文件。
- `level` (str): 文件日志的级别 (默认 "INFO")。

### 2. 管道框架 (Pipeline Framework)

提供基于 Node 的流式处理框架，支持上下文共享与状态持久化。

#### Python API

```python
from bio_analyze_core.pipeline import Pipeline, Node, Context, Progress

class MyNode(Node):
    def run(self, context: Context, progress: Progress, logger):
        logger.info(f"Processing {context.data}")
        progress.update(message="Working...", percentage=50)
        context.result = "done"

# 创建流程
pipeline = Pipeline("my_pipeline", state_file="pipeline_state.json")
pipeline.context.data = "input_data"

# 添加节点
pipeline.add_node(MyNode("step1"))

# 运行
pipeline.run()
```

### 3. 子进程管理 (Subprocess)

封装 `subprocess.run`，提供更安全的外部命令执行与输出捕获。

#### Python API

```python
from bio_analyze_core.subprocess import run, CalledProcessError

try:
    result = run(
        ["ls", "-la"],
        cwd="./",
        check=True,          # 非零退出码抛出异常
        capture_output=True  # 捕获 stdout/stderr
    )
    print(result.stdout)
except CalledProcessError as e:
    print(f"Command failed: {e.stderr}")
```

### 4. 配置管理 (Configuration)

支持从 JSON/YAML 加载配置，并提供深层合并工具。

#### Python API

```python
from bio_analyze_core.utils import load_config

# 自动识别 .json 或 .yaml
config = load_config("config.yaml")
print(config["input_dir"])
```
