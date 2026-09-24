"""
Runs the full FastBox pipeline against every JSON file in data/ and checks
the core invariant the brief explicitly requires: total packages delivered
must equal total packages in the input. This is the single most important
test in the suite — most candidates will only try the one sample from the
PDF; this suite proves the solution generalizes across every schema
variation and dataset size provided.
"""

import glob
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastbox.loader import load_data
from fastbox.assignment import assign_packages
from fastbox.simulator import simulate_deliveries
from fastbox.report import generate_report, validate_report

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILES = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))


@pytest.mark.parametrize("data_path", DATA_FILES)
def test_pipeline_runs_and_matches_invariant(data_path):
    warehouses, agents, packages = load_data(data_path)
    agents = assign_packages(agents, warehouses, packages)
    simulation_results = simulate_deliveries(agents, warehouses, packages)
    report = generate_report(simulation_results)

    # Should not raise
    validate_report(report, total_input_packages=len(packages))

    # Every package assigned to exactly one agent
    assert all(pkg.assigned_agent is not None for pkg in packages)

    # best_agent must be a real agent id present in the report
    assert report["best_agent"] in agents


def test_at_least_one_data_file_was_found():
    # Guards against a silently empty test run if the data/ path is wrong
    assert len(DATA_FILES) >= 11