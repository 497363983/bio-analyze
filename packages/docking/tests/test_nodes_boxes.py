from unittest.mock import patch

from bio_analyze_docking.api import run_docking_batch


def test_batch_docking_node_with_boxes(tmp_path):
    rec_dir = tmp_path / "receptors"
    rec_dir.mkdir()
    lig_dir = tmp_path / "ligands"
    lig_dir.mkdir()
    out_dir = tmp_path / "output"

    rec1 = rec_dir / "rec1.pdbqt"
    rec1.write_text("ATOM")
    rec2 = rec_dir / "rec2.pdbqt"
    rec2.write_text("ATOM")

    lig1 = lig_dir / "lig1.sdf"
    lig1.write_text("ATOM")

    boxes = {
        "rec1.pdbqt": {
            "center_x": 1.0,
            "center_y": 2.0,
            "center_z": 3.0,
            "size_x": 10.0,
            "size_y": 10.0,
            "size_z": 10.0,
        },
        "rec2": {
            "center_x": 4.0,
            "center_y": 5.0,
            "center_z": 6.0,
            "size_x": 20.0,
            "size_y": 20.0,
            "size_z": 20.0,
        },
    }

    # We patch run_docking_task inside nodes.py to capture the center and size
    with patch("bio_analyze_docking.nodes.run_docking_task") as mock_task:
        # Mock the result of the task to avoid exceptions
        mock_task.return_value = {
            "status": "success",
            "receptor": "rec1",
            "ligand": "lig1",
            "box_center": [0, 0, 0],
            "box_size": [0, 0, 0],
        }

        # Call the batch pipeline
        results = run_docking_batch(
            receptors=rec_dir,
            ligands=lig_dir,
            output_dir=out_dir,
            center=[0.0, 0.0, 0.0],
            size=[15.0, 15.0, 15.0],
            boxes=boxes,
            engine="vina",
        )

        assert mock_task.call_count == 2

        # Verify the arguments passed to run_docking_task
        calls = mock_task.call_args_list

        rec1_call = next(call for call in calls if call.args[3] == "rec1.pdbqt")
        rec2_call = next(call for call in calls if call.args[3] == "rec2.pdbqt")

        # For rec1.pdbqt
        assert rec1_call.args[5] == [1.0, 2.0, 3.0]  # center
        assert rec1_call.args[6] == [10.0, 10.0, 10.0]  # size

        # For rec2.pdbqt (matches by stem 'rec2')
        assert rec2_call.args[5] == [4.0, 5.0, 6.0]  # center
        assert rec2_call.args[6] == [20.0, 20.0, 20.0]  # size
