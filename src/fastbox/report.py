"""
Report generation.

ASSUMPTION (documented per assignment instructions):
"efficiency" = total_distance / packages_delivered. Lower is better — this
matches the sample report in the brief, where the agent with the lowest
efficiency value is chosen as best_agent, even though the name reads as if
higher should be better.

EDGE CASE:
An agent who was assigned zero packages would cause a divide-by-zero on
efficiency, and trivially "win" best_agent with a 0.0 total_distance if not
handled explicitly. Such agents are reported with packages_delivered = 0,
total_distance = 0.0, efficiency = None, and are excluded from the
best_agent comparison entirely.
"""

from typing import Dict


def generate_report(simulation_results: Dict[str, dict]) -> dict:
    """
    Build the final report dict matching the structure shown in the brief:
        {
            "A1": {"packages_delivered": 2, "total_distance": 85.32, "efficiency": 42.66},
            ...
            "best_agent": "A1"
        }
    """
    report = {}
    best_agent = None
    best_efficiency = None

    for aid, stats in simulation_results.items():
        delivered = stats["packages_delivered"]
        distance = stats["total_distance"]

        if delivered == 0:
            efficiency = None
        else:
            efficiency = round(distance / delivered, 2)

        report[aid] = {
            "packages_delivered": delivered,
            "total_distance": distance,
            "efficiency": efficiency,
        }

        # Lower efficiency = better. Skip agents with no deliveries.
        if efficiency is not None:
            if best_efficiency is None or efficiency < best_efficiency:
                best_efficiency = efficiency
                best_agent = aid

    report["best_agent"] = best_agent
    return report


def validate_report(report: dict, total_input_packages: int):
    """
    Hard invariant check required by the brief: total packages delivered
    across all agents must equal total packages in the input.
    Raises AssertionError if violated, so a broken simulation fails loudly
    instead of silently producing a wrong report.
    """
    delivered_sum = sum(
        v["packages_delivered"] for k, v in report.items() if k != "best_agent"
    )
    assert delivered_sum == total_input_packages, (
        f"Invariant violated: {delivered_sum} packages delivered in report, "
        f"but input had {total_input_packages} packages."
    )