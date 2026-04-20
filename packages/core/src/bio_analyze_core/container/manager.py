"""
Docker container lifecycle management and API encapsulation.
"""

import sys
import threading
import time
from typing import Any

try:
    import docker
    from docker.errors import APIError, DockerException, NotFound
    from docker.models.containers import Container
except ImportError:
    docker = None
    APIError = DockerException = NotFound = Exception
    Container = Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from bio_analyze_core.logging import get_logger

from .exceptions import (
    ContainerExecutionError,
    ContainerTimeoutError,
    ImageBuildError,
    DockerNotAvailableError,
    ImagePullError,
)
from .models import ContainerConfig

logger = get_logger(__name__)

class ContainerManager:
    """
    Encapsulates Docker API, supporting retries, connection pools, and lifecycle monitoring.
    """

    def __init__(self, base_url: str | None = None):
        """
        Initialize Docker client.
        """
        if docker is None:
            raise DockerNotAvailableError("Docker python SDK is not installed.")
        try:
            # `from_env` automatically sets up connection pooling via requests.
            # You can also pass `version="auto"`.
            if base_url:
                self.client = docker.DockerClient(base_url=base_url, version="auto")
            else:
                self.client = docker.from_env(version="auto")

            # 探测 Docker 是否可用
            self.client.ping()
        except DockerException as e:
            raise DockerNotAvailableError(f"Docker daemon is not available: {e}") from e

    @retry(
        retry=retry_if_exception_type(APIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def pull_image(self, image_name: str) -> None:
        """
        Pull the specified image, with exponential backoff retry.
        """
        logger.info(f"Checking image: {image_name}")
        try:
            self.client.images.get(image_name)
            logger.debug(f"Image {image_name} already exists locally.")
        except NotFound:
            logger.info(f"Pulling image {image_name}... This may take a while.")
            try:
                # Streaming the pull logs to show progress could be done,
                # but simple block pull is safer for background scripts.
                for line in self.client.api.pull(image_name, stream=True, decode=True):
                    if "status" in line:
                        logger.debug(f"Pulling {image_name}: {line['status']}")
            except DockerException as e:
                raise ImagePullError(f"Failed to pull image {image_name}: {e}") from e

    def create_container(self, config: ContainerConfig) -> "Container":
        """
        Create a Docker container based on the configuration.
        """
        volumes = {
            vol.host_path: {
                "bind": vol.container_path,
                "mode": vol.mode,
            }
            for vol in config.volumes
        }

        host_config_kwargs = {}
        if config.cpu_quota is not None:
            host_config_kwargs["cpu_quota"] = config.cpu_quota
        if config.cpu_period is not None:
            host_config_kwargs["cpu_period"] = config.cpu_period
        if config.mem_limit is not None:
            host_config_kwargs["mem_limit"] = config.mem_limit

        logger.debug(f"Creating container with image {config.image}, cmd: {config.command}")

        try:
            container = self.client.containers.create(
                image=config.image,
                command=config.command,
                volumes=volumes,
                working_dir=config.working_dir,
                environment=config.environment,
                detach=True,
                **host_config_kwargs
            )
            return container
        except DockerException as e:
            raise RuntimeError(f"Failed to create container: {e}") from e

    def build_image(self, image_name: str, build_context: str, dockerfile: str = "Dockerfile") -> None:
        """Build a Docker image from a local context."""
        logger.info(f"Building image {image_name} from {build_context} using {dockerfile}")
        try:
            _, build_logs = self.client.images.build(
                path=build_context,
                dockerfile=dockerfile,
                tag=image_name,
                rm=True,
                decode=True,
            )
            for line in build_logs:
                if "stream" in line:
                    logger.debug(line["stream"].rstrip())
        except DockerException as e:
            raise ImageBuildError(f"Failed to build image {image_name}: {e}") from e

    def start_container(self, container: "Container") -> None:
        """
        Start the container.
        """
        try:
            container.start()
        except DockerException as e:
            raise RuntimeError(f"Failed to start container {container.id}: {e}") from e

    def stop_container(self, container: "Container", timeout: int = 10) -> None:
        """
        Stop the container.
        """
        try:
            container.stop(timeout=timeout)
        except DockerException as e:
            logger.warning(f"Failed to stop container {container.id}: {e}")

    def remove_container(self, container: "Container", force: bool = True) -> None:
        """
        Remove the container.
        """
        try:
            container.remove(force=force)
        except DockerException as e:
            logger.warning(f"Failed to remove container {container.id}: {e}")

    def monitor_logs_and_wait(self, container: "Container", timeout: float | None = None) -> int:
        """
        Block and wait for container execution, stream logs, handle timeout, and return exit code.
        """
        # Stream logs in a background thread
        def stream_logs():
            try:
                for line in container.logs(stream=True, follow=True):
                    # Remove trailing newlines and decode if bytes
                    text = line.decode('utf-8', errors='replace').rstrip() if isinstance(line, bytes) else line.rstrip()
                    # We output to sys.stderr or logger to ensure it is visible
                    print(text, file=sys.stderr, flush=True)
            except Exception as e:
                logger.debug(f"Log streaming interrupted: {e}")

        log_thread = threading.Thread(target=stream_logs, daemon=True)
        log_thread.start()

        start_time = time.time()

        while True:
            container.reload()
            status = container.status

            if status == "exited":
                # Get the exit code
                result = container.wait()
                exit_code = result.get("StatusCode", -1)

                # Wait a bit for log stream to finish
                log_thread.join(timeout=2.0)

                return exit_code

            if status in ("dead", "removing"):
                return -1

            if timeout is not None and (time.time() - start_time) > timeout:
                # Timeout
                self.stop_container(container)
                raise ContainerTimeoutError(f"Container execution timed out after {timeout} seconds.")

            time.sleep(0.5)

    def run_task(self, config: ContainerConfig, remove: bool = True) -> None:
        """
        High-level API: Execute full lifecycle (pull, create, start, monitor, cleanup).
        """
        if config.build_context:
            self.build_image(
                config.image,
                build_context=config.build_context,
                dockerfile=config.dockerfile,
            )
        else:
            self.pull_image(config.image)
        container = self.create_container(config)

        try:
            self.start_container(container)
            logger.info(f"Container {container.short_id} started.")

            exit_code = self.monitor_logs_and_wait(container, timeout=config.timeout)

            if exit_code != 0:
                # Fetch last 50 lines of logs for the exception
                try:
                    logs_bytes = container.logs(tail=50)
                    logs = logs_bytes.decode('utf-8', errors='replace')
                except Exception:
                    logs = "Failed to fetch logs."

                raise ContainerExecutionError(
                    message=f"Container exited with code {exit_code}.",
                    exit_code=exit_code,
                    logs=logs
                )

            logger.info(f"Container {container.short_id} completed successfully.")

        finally:
            if remove:
                logger.debug(f"Cleaning up container {container.short_id}...")
                self.remove_container(container, force=True)
