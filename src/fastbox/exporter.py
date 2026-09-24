"""
Bonus feature: export the top-performing agent to CSV.
"""

import csv


def export_top_performer_csv(report: dict, output_path: str = "top_performer.csv"):
    """
    Write the best_agent's stats to a simple CSV file.
    """
    best_agent_id = report.get("best_agent")
    if best_agent_id is None:
        # No agent delivered anything — nothing meaningful to export
        return None

    stats = report[best_agent_id]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["agent_id", "packages_delivered", "total_distance", "efficiency"])
        writer.writerow([
            best_agent_id,
            stats["packages_delivered"],
            stats["total_distance"],
            stats["efficiency"],
        ])

    return output_path