import os
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any

from rich.progress import BarColumn, TaskProgressColumn, TextColumn, TimeRemainingColumn
from rich.progress import Progress as RichProgress

from .logging import get_logger
from .utils import safe_load_json, safe_save_json


class Context(dict):
    """
    Context dictionary for sharing data between pipeline nodes.
    """

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"'Context' object has no attribute '{item}'") from None

    def __setattr__(self, key, value):
        self[key] = value

    def set_save_callback(self, callback):
        """
        Set callback function for saving state.

        Args:
            callback (callable):
                Callback function.
        """
        self._save_callback = callback

    def checkpoint(self):
        """
        Trigger saving current pipeline state (checkpoint).
        """
        if hasattr(self, "_save_callback") and self._save_callback:
            self._save_callback()

class Progress:
    """
    Class for reporting task progress using rich library.
    """

    def __init__(self):
        self._progress = RichProgress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        )
        self._task_id = None

    def __enter__(self):
        self._progress.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self._progress.stop()

    def start_task(self, description: str, total: float = 100):
        """
        Start a new task with description.

        Args:
            description (str):
                Task description.
            total (float, optional):
                Total progress value. Defaults to 100.
        """
        if self._task_id is not None:
            self._progress.remove_task(self._task_id)
        self._task_id = self._progress.add_task(description, total=total)

    def update(self, message: str | None = None, percentage: float | None = None):
        """
        Update progress and message of current task.

        Args:
            message (str, optional):
                Progress message description.
            percentage (float, optional):
                Completion percentage (0-100).
        """
        if self._task_id is None:
            return

        kwargs = {}
        if message:
            kwargs["description"] = message
        if percentage is not None:
            kwargs["completed"] = percentage

        self._progress.update(self._task_id, **kwargs)

class Node(ABC):
    """
    Abstract base class for pipeline nodes.

    Attributes:
        name (str):
            Node name.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, context: Context, progress: Progress, logger: Any):
        """
        Execute node logic.

        Args:
            context (Context):
                Pipeline context object.
            progress (Progress):
                Progress reporter.
            logger (Any):
                Logger instance.
        """
        pass

class Pipeline:
    """
    Pipeline class for linear execution of nodes, supporting state saving and restoration.

    Attributes:
        name (str):
            Pipeline name.
        state_file (str):
            Path to state file.
        nodes (list[Node]):
            List of nodes.
        context (Context):
            Context data.
    """

    def __init__(self, name: str, state_file: str):
        self.name = name
        self.state_file = state_file
        self.nodes: list[Node] = []
        self.context = Context()
        self.logger = get_logger(name)
        self._completed_nodes: list[str] = []

    def add_node(self, node: Node):
        """
        Add a node to the pipeline.

        Args:
            node (Node):
                Node instance to add.
        """
        self.nodes.append(node)

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                data = safe_load_json(self.state_file)
                self._completed_nodes = data.get("completed_nodes", [])
                # 需要小心不要用旧数据覆盖初始上下文参数，如果我们不想这样的话。
                # 但通常恢复意味着我们需要旧状态。
                # 然而，如果用户更改了一些参数，我们可能会有冲突。
                # 当前策略：使用保存的状态更新上下文。
                self.context.update(data.get("context", {}))
                self.logger.info(f"Loaded state from {self.state_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load state file: {e}")

    def _save_state(self):
        context_data = self.context.copy()
        if "_save_callback" in context_data:
            del context_data["_save_callback"]

        data = {
            "completed_nodes": self._completed_nodes,
            "all_nodes": [node.name for node in self.nodes],
            "context": context_data,
        }
        try:
            safe_save_json(data, self.state_file)
        except Exception as e:
            self.logger.error(f"Failed to save state file: {e}")

    def run(self):
        self._load_state()
        self.context.set_save_callback(self._save_state)

        # 即使加载了状态，我们也需要确保存储的 all_nodes 信息是最新的
        # 但是在 _save_state 中会每次重新生成 all_nodes 列表，所以这里不需要特别处理

        with Progress() as progress:
            for node in self.nodes:
                if node.name in self._completed_nodes:
                    self.logger.info(f"Skipping completed node: {node.name}")
                    if hasattr(node, "skip"):
                        node.skip()
                    continue

                self.logger.info(f"Running node: {node.name}")
                progress.start_task(f"Running {node.name}...", total=100)

                try:
                    node.run(self.context, progress, self.logger)
                    progress.update(percentage=100)
                    self._completed_nodes.append(node.name)
                    self._save_state()
                except Exception as e:
                    self.logger.error(f"Node {node.name} failed: {e}")
                    raise
