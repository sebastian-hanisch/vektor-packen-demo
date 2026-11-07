"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vkp_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Fünf Teile (Volumen, Gewicht) = (6, 2), (2, 7), (5, 5), (4, 3), (3, 4) mit den Nummern 0 bis 4, Kapazität 10 in beiden Maßen.

    Von Hand gerechnet (Details in tests/test_algorithm.py): Summe der Volumen 20, der Gewichte 21, Schranke 3 (die Gewichte brauchen drei Behälter), Optimum 3
    (Zerlegung {0, 1}, {2, 3}, {4})."""
    return Instance(((6, 2), (2, 7), (5, 5), (4, 3), (3, 4)), 10)
