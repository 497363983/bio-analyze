from bio_analyze_core.i18n import _
"""Test Docker container lifecycle management and path mapping logic. """
import os
import sys
from pathlib import Path
from unittest import mock

import pytest
from bio_analyze_core.container.exceptions import (
    ContainerExecutionError,
    DockerNotAvailableError,
)
from bio_analyze_core.container.manager import ContainerManager
from bio_analyze_core.container.models import ContainerConfig
from bio_analyze_core.container.runner import run_pipeline_in_container
from bio_analyze_core.pipeline import Context, Pipeline


@pytest.fixture
def mock_docker_client():
    """Mock docker.DockerClient to avoid actual docker daemon requirement."""
    with mock.patch("bio_analyze_core.container.manager.docker") as mock_docker:
        mock_client_instance = mock.Mock()
        mock_docker.from_env.return_value = mock_client_instance
        yield mock_docker, mock_client_instance


def test_container_manager_init(mock_docker_client):
    mock_docker, mock_client = mock_docker_client
    
    # Success init
    manager = ContainerManager()
    assert manager.client is mock_client
    mock_client.ping.assert_called_once()
    
    # Init fails if docker not installed
    with mock.patch("bio_analyze_core.container.manager.docker", None):
        with pytest.raises(DockerNotAvailableError):
            ContainerManager()


def test_container_manager_run_task(mock_docker_client):
    mock_docker, mock_client = mock_docker_client
    
    manager = ContainerManager()
    config = ContainerConfig(
        image="test-image",
        command=["echo", "hello"],
        cpu_quota=100000,
    )
    
    mock_container = mock.Mock()
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = [b"hello\n"]
    
    mock_client.containers.create.return_value = mock_container
    
    # Patch monitor_logs_and_wait to return 0 immediately
    with mock.patch.object(manager, "monitor_logs_and_wait", return_value=0):
        manager.run_task(config)
        
    mock_client.containers.create.assert_called_once()
    mock_container.start.assert_called_once()
    mock_container.remove.assert_called_once_with(force=True)


def test_container_manager_run_task_with_build(mock_docker_client):
    mock_docker, mock_client = mock_docker_client
    
    manager = ContainerManager()
    config = ContainerConfig(
        image="test-image",
        command=["echo", "hello"],
        build_context="/path/to/context",
        dockerfile="CustomDockerfile"
    )
    
    mock_container = mock.Mock()
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = [b"hello\n"]
    
    mock_client.containers.create.return_value = mock_container
    # Mock build
    mock_client.images.build.return_value = (mock.Mock(), [{"stream": "step 1"}])
    
    with mock.patch.object(manager, "monitor_logs_and_wait", return_value=0):
        manager.run_task(config)
        
    mock_client.images.build.assert_called_once_with(
        path="/path/to/context",
        dockerfile="CustomDockerfile",
        tag="test-image",
        rm=True,
        decode=True
    )
    mock_client.containers.create.assert_called_once()
    mock_container.start.assert_called_once()
    mock_container.remove.assert_called_once_with(force=True)

def test_container_manager_run_task_failure(mock_docker_client):
    mock_docker, mock_client = mock_docker_client
    
    manager = ContainerManager()
    config = ContainerConfig(image="test-image", command=["fail"])
    
    mock_container = mock.Mock()
    mock_client.containers.create.return_value = mock_container
    
    with mock.patch.object(manager, "monitor_logs_and_wait", return_value=1):
        mock_container.logs.return_value = b"error message"
        with pytest.raises(ContainerExecutionError) as exc:
            manager.run_task(config)
            
        assert exc.value.exit_code == 1
        assert "error message" in exc.value.logs


def test_run_pipeline_in_container_skip_if_already_in_container():
    with mock.patch.dict(os.environ, {"BIO_ANALYZE_IN_CONTAINER": "1"}):
        pipeline = mock.Mock()
        assert not run_pipeline_in_container(pipeline)


def test_run_pipeline_in_container_fallback_if_docker_not_available():
    pipeline = mock.Mock()
    pipeline.context.use_container = True
    
    with mock.patch("bio_analyze_core.container.runner.ContainerManager", side_effect=DockerNotAvailableError("test")):
        assert not run_pipeline_in_container(pipeline)


@mock.patch("bio_analyze_core.container.runner.ContainerManager")
def test_run_pipeline_in_container_success(MockContainerManager, tmp_path):
    # Setup mock pipeline
    pipeline = Pipeline("test_pipeline", str(tmp_path / "state.json"))
    pipeline.context.use_container = True
    pipeline.context.threads = 8
    
    mock_manager = MockContainerManager.return_value
    
    # Create some dummy files to test path replacement
    test_file = tmp_path / "test.txt"
    test_file.touch()
    
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    
    original_argv = sys.argv.copy()
    
    try:
        # Simulate CLI arguments with absolute paths
        sys.argv = ["bioanalyze", "run", "--input", str(test_dir), "--file", str(test_file)]
        
        result = run_pipeline_in_container(pipeline)
        
        assert result is True
        mock_manager.run_task.assert_called_once()
        
        config = mock_manager.run_task.call_args[0][0]
        assert isinstance(config, ContainerConfig)
        
        # Check if CPU quota is set properly (8 threads * 100000)
        assert config.cpu_quota == 800000
        
        # Check volumes
        assert len(config.volumes) > 0
        
        # Check command replacement
        assert "bioanalyze" in config.command
        assert "run" in config.command
        assert "--input" in config.command
        assert "--file" in config.command
        
        # The absolute paths should be replaced by container paths like /mnt/vol_0
        assert str(test_dir) not in config.command
        assert str(test_file) not in config.command
        
        # The container command should have /mnt/vol_x strings
        vol_paths = [arg for arg in config.command if "/mnt/vol_" in arg]
        assert len(vol_paths) == 2
        
    finally:
        sys.argv = original_argv
