"""
FastBox Delivery System — CLI entry point.

Usage:
    python main.py --input data/base_case.json --output report.json
"""

import argparse
import json
import sys

sys.path.insert(0, "src")

from fastbox.loader import load_data
from fastbox.assignment import assign_packages
from fastbox.simulator import simulate_deliveries
from fastbox.report import generate_report, validate_report


def run(input_path: str, output_path: str):
    warehouses, agents, packages = load_data(input_path)
    agents = assign_packages(agents, warehouses, packages)
    simulation_results = simulate_deliveries(agents, warehouses, packages)
    report = generate_report(simulation_results)
    validate_report(report, total_input_packages=len(packages))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Report written to {output_path}")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FastBox delivery simulator")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", default="report.json", help="Path to write the report JSON")
    args = parser.parse_args()

    run(args.input, args.output)