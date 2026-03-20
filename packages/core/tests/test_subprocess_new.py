import sys
import time
import pytest
from bio_analyze_core.subprocess import run, run_streaming, TimeoutExpired, CalledProcessError

def test_run_success():
    res = run([sys.executable, "-c", "print('hello world')"])
    assert res.returncode == 0
    assert "hello world" in res.stdout

def test_run_timeout():
    with pytest.raises(TimeoutExpired) as exc:
        run([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.5)
    assert exc.value.timeout == 0.5

def test_run_tail_lines():
    script = "for i in range(100): print(f'line {i}')\nimport sys; sys.exit(1)"
    with pytest.raises(CalledProcessError) as exc:
        run([sys.executable, "-c", script], tail_lines=10)
    assert "line 99" in exc.value.output
    assert len(exc.value.output.strip().split('\n')) == 10

def test_run_streaming_success():
    lines = []
    def on_line(line):
        lines.append(line)
    res = run_streaming([sys.executable, "-c", "print('hello'); print('world')"], on_line)
    assert res.returncode == 0
    assert lines == ["hello", "world"]

def test_run_streaming_timeout():
    lines = []
    def on_line(line):
        lines.append(line)
    with pytest.raises(TimeoutExpired) as exc:
        run_streaming([sys.executable, "-c", "import time; print('start', flush=True); time.sleep(2); print('end')"], on_line, timeout=0.5)
    assert lines == ["start"]
    assert exc.value.timeout == 0.5
