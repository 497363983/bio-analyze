from bio_analyze_core.i18n import _
"""Define configuration and model data classes for Docker containers. """
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VolumeMount:
    """Describes volume mount mapping between container and host. """
    host_path: str
    container_path: str
    mode: str = "rw"  # "rw" for read-write, "ro" for read-only


@dataclass
class ContainerConfig:
    """Runtime configuration and resource limits for the container. """
    image: str
    command: list[str]
    volumes: list[VolumeMount] = field(default_factory=list)
    working_dir: Optional[str] = None
    environment: dict[str, str] = field(default_factory=dict)
    
    # Image Building
    build_context: Optional[str] = None
    dockerfile: str = "Dockerfile"
    
    # Resource Limits
    cpu_quota: Optional[int] = None
    cpu_period: Optional[int] = 100000
    mem_limit: Optional[str] = None  # e.g., "4g"
    
    # Timeout
    timeout: Optional[float] = None
