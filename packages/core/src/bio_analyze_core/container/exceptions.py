"""Define exception classes related to Docker container operations."""
class DockerNotAvailableError(Exception):
    """Raised when the Docker daemon is not running or not installed."""
    pass

class ImagePullError(Exception):
    """Raised when pulling a Docker image fails."""
    pass

class ImageBuildError(Exception):
    """Raised when building a Docker image fails."""
    pass

class ContainerExecutionError(Exception):
    """
    Raised when the task inside the container fails with a non-zero exit code.

    Attributes:
        exit_code (int): The exit code of the container.
        logs (str): Tail logs captured before the container exited.
    """
    def __init__(self, message: str, exit_code: int, logs: str):
        super().__init__(message)
        self.exit_code = exit_code
        self.logs = logs

    def __str__(self):
        return f"{super().__str__()}\nExit Code: {self.exit_code}\nLogs:\n{self.logs}"

class ContainerTimeoutError(Exception):
    """Raised when the container execution times out."""
    pass
