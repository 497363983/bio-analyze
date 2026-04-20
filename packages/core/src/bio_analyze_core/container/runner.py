"""Provide logic to run a Pipeline inside a Docker container."""
import os
import sys
from pathlib import Path
from typing import Any

from bio_analyze_core.logging import get_logger

from .exceptions import DockerNotAvailableError
from .manager import ContainerManager
from .models import ContainerConfig, VolumeMount

logger = get_logger(__name__)

def run_pipeline_in_container(pipeline: Any) -> bool:
    """
    Attempt to execute the current pipeline task in a Docker container.

    Args:
        pipeline: The Pipeline instance.

    Returns:
        bool: True if execution succeeded in a container, otherwise False.
    """
    if os.environ.get("BIO_ANALYZE_IN_CONTAINER") == "1":
        # Already inside container
        return False

    use_container = getattr(pipeline.context, "use_container", False)
    if not use_container:
        return False

    try:
        manager = ContainerManager()
    except DockerNotAvailableError:
        logger.warning("Docker is not available. Falling back to local execution.")
        return False

    # Extract paths from context to create volume mounts
    volumes = []

    # Always mount current working directory
    cwd = Path.cwd().resolve()
    container_cwd = "/mnt/workspace"
    volumes.append(VolumeMount(host_path=str(cwd), container_path=container_cwd, mode="rw"))

    # Find all absolute paths in sys.argv
    new_argv = []
    vol_index = 0
    for arg in sys.argv:
        # Check if arg is an existing absolute path
        p = Path(arg)
        if p.is_absolute() and p.exists():
            # Create a mount for it
            container_path = f"/mnt/vol_{vol_index}"
            # If it's a file, mount its parent directory to be safe
            if p.is_file():
                host_dir = str(p.parent)
                container_dir = container_path
                volumes.append(VolumeMount(host_path=host_dir, container_path=container_dir, mode="rw"))
                new_argv.append(f"{container_dir}/{p.name}")
            else:
                volumes.append(VolumeMount(host_path=str(p), container_path=container_path, mode="rw"))
                new_argv.append(container_path)
            vol_index += 1
        else:
            new_argv.append(arg)

    # Determine image name and build context
    # We can get it from context or use a default standard image
    image = getattr(pipeline.context, "container_image", "bio-analyze-env:latest")
    build_context = getattr(pipeline.context, "container_build_context", None)
    dockerfile = getattr(pipeline.context, "container_dockerfile", "Dockerfile")

    # Resource limits
    threads = getattr(pipeline.context, "threads", 4)
    mem_limit = getattr(pipeline.context, "mem_limit", None) # e.g. "16g"

    config = ContainerConfig(
        image=image,
        command=new_argv,
        volumes=volumes,
        working_dir=container_cwd,
        environment={
            "BIO_ANALYZE_IN_CONTAINER": "1",
            "LANG": "C.UTF-8",
        },
        build_context=build_context,
        dockerfile=dockerfile,
        cpu_quota=threads * 100000,
        cpu_period=100000,
        mem_limit=mem_limit,
    )

    logger.info(f"Submitting pipeline task to Docker container (image: {image})...")

    # Run task and wait
    # This will raise ContainerExecutionError if the container fails
    manager.run_task(config, remove=True)

    return True
