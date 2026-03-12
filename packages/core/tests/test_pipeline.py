import json

import pytest

from bio_analyze_core.pipeline import Node, Pipeline


class MockNode(Node):
    def __init__(self, name, action=None):
        super().__init__(name)
        self.action = action
        self.executed = False
        self.skipped = False

    def run(self, context, progress, logger):
        if self.action:
            self.action(context)
        self.executed = True

    def skip(self):
        self.skipped = True

    def next(self):
        pass


def test_pipeline_sequential_execution(tmp_path):
    state_file = tmp_path / "state.json"
    pipeline = Pipeline("test_pipeline", str(state_file))

    node1 = MockNode("node1", lambda ctx: ctx.update({"step1": "done"}))
    node2 = MockNode("node2", lambda ctx: ctx.update({"step2": "done"}))

    pipeline.add_node(node1)
    pipeline.add_node(node2)

    pipeline.run()

    assert node1.executed
    assert node2.executed
    assert pipeline.context["step1"] == "done"
    assert pipeline.context["step2"] == "done"


def test_pipeline_persistence_and_resume(tmp_path):
    state_file = tmp_path / "resume_state.json"

    # First run: node1 runs, then crash
    pipeline1 = Pipeline("resume_pipeline", str(state_file))
    node1 = MockNode("node1", lambda ctx: ctx.update({"step1": "done"}))

    class FailingNode(Node):
        def run(self, context, progress, logger):
            raise RuntimeError("Crash!")

        def next(self):
            pass

    failing_node = FailingNode("failing_node")
    node2 = MockNode("node2", lambda ctx: ctx.update({"step2": "done"}))

    pipeline1.add_node(node1)
    pipeline1.add_node(failing_node)
    pipeline1.add_node(node2)

    with pytest.raises(RuntimeError):
        pipeline1.run()

    assert node1.executed
    assert pipeline1.context["step1"] == "done"

    # Verify state file
    with open(state_file) as f:
        state = json.load(f)
        assert "node1" in state["completed_nodes"]
        assert "failing_node" not in state["completed_nodes"]
        assert state["context"]["step1"] == "done"

    # Resume
    pipeline2 = Pipeline("resume_pipeline", str(state_file))

    # Recreate nodes. node1 should be skipped.
    node1_retry = MockNode("node1", lambda ctx: ctx.update({"step1": "retry"}))

    # We replace failing_node with a success one (simulating fix)
    fixed_node = MockNode("failing_node", lambda ctx: ctx.update({"fixed": "yes"}))

    node2_retry = MockNode("node2", lambda ctx: ctx.update({"step2": "done"}))

    pipeline2.add_node(node1_retry)
    pipeline2.add_node(fixed_node)
    pipeline2.add_node(node2_retry)

    pipeline2.run()

    assert node1_retry.skipped
    assert not node1_retry.executed

    assert fixed_node.executed
    assert node2_retry.executed

    assert pipeline2.context["step1"] == "done"  # Should be from state, not "retry"
    assert pipeline2.context["fixed"] == "yes"
    assert pipeline2.context["step2"] == "done"


def test_pipeline_checkpoint(tmp_path):
    state_file = tmp_path / "checkpoint_state.json"

    class LongRunningNode(Node):
        def run(self, context, progress, logger):
            # Simulate step 1
            context.progress_step = 1
            context.checkpoint()

            # Simulate step 2
            context.progress_step = 2
            context.checkpoint()

            # Crash
            raise RuntimeError("Crash after checkpoint")

        def next(self):
            pass

    pipeline = Pipeline("checkpoint_pipeline", str(state_file))
    node = LongRunningNode("long_node")
    pipeline.add_node(node)

    with pytest.raises(RuntimeError):
        pipeline.run()

    # Verify state file contains intermediate state
    with open(state_file) as f:
        state = json.load(f)
        assert "long_node" not in state["completed_nodes"]
        assert state["context"]["progress_step"] == 2
