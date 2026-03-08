import json
from pathlib import Path
from bio_plot.theme import PlotTheme, set_theme
import matplotlib.pyplot as plt
import seaborn as sns

def test_load_theme_from_json(tmp_path):
    # Create a custom theme JSON
    theme_data = {
        "name": "custom_json",
        "context": "poster",
        "style": "darkgrid",
        "rc_params": {
            "lines.linewidth": 5.0
        }
    }
    json_path = tmp_path / "my_theme.json"
    with open(json_path, "w") as f:
        json.dump(theme_data, f)
        
    # Apply theme
    set_theme(str(json_path))
    
    # Check if applied
    assert sns.axes_style()["axes.grid"] == True # darkgrid has grid
    assert plt.rcParams["lines.linewidth"] == 5.0
    
def test_load_theme_from_py_file(tmp_path):
    # Create a custom theme Python file
    py_content = """
from bio_plot.theme import PlotTheme

MY_THEME = PlotTheme(
    name="custom_py",
    style="whitegrid",
    rc_params={"lines.markersize": 10.0}
)
"""
    py_path = tmp_path / "my_theme.py"
    py_path.write_text(py_content)
    
    # Apply theme
    set_theme(str(py_path))
    
    # Check
    assert sns.axes_style()["axes.grid"] == True # whitegrid has grid
    assert plt.rcParams["lines.markersize"] == 10.0

def test_fallback_to_default():
    set_theme("non_existent_theme")
    # Default is ticks (no grid usually) or check specific param
    # THEMES["default"] uses "ticks"
    assert sns.axes_style()["axes.facecolor"] == 'white'
