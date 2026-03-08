import pytest
from bio_plot.theme import THEMES

def test_themes():
    assert 'nature' in THEMES
    assert 'science' in THEMES
