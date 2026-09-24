"""
Distance calculation and nearest-agent package assignment.

ASSUMPTION (documented per assignment instructions):
When multiple agents are equidistant from a package's warehouse, ties are
broken by:
  1. Preferring the agent with fewer packages already assigned (load balancing)
  2. If still tied, preferring the alphabetically-lowest agent ID
This guarantees the same input always produces the same output.
"""

import math
from typing import Dict, List

from .models import Warehouse, Agent, Package


def euclidean_distance(p1, p2) -> float:
    """Straight-line distance between two (x, y) points. Used everywhere
    distance needs to be computed, so the formula lives in exactly one place."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def build_distance_matrix(agents: Dict[str, Agent], warehouses: Dict[str, Warehouse]):
    """
    Precompute every agent->warehouse distance once, O(agents x warehouses).
    Avoids redundantly recalculating the same agent-warehouse distance for
    every package that happens to share a warehouse — a small dataset here,
    but the right scalable pattern as package/agent counts grow.
    """
    matrix = {}
    for aid, agent in agents.items():
        matrix[aid] = {}
        for wid, warehouse in warehouses.items():
            matrix[aid][wid] = euclidean_distance(agent.location, warehouse.location)
    return matrix


def assign_packages(
    agents: Dict[str, Agent],
    warehouses: Dict[str, Warehouse],
    packages: List[Package],
) -> Dict[str, Agent]:
    """
    Assign each package to the agent nearest to its pickup warehouse.
    Mutates and returns `agents`, with each Agent's `packages_assigned`
    filled in, and sets `assigned_agent` on each Package.
    """
    distance_matrix = build_distance_matrix(agents, warehouses)

    for pkg in packages:
        candidates = []
        for aid in agents:
            dist = distance_matrix[aid][pkg.warehouse_id]
            candidates.append((dist, len(agents[aid].packages_assigned), aid))

        # Sort by: distance asc, then current load asc, then agent id asc
        candidates.sort(key=lambda c: (c[0], c[1], c[2]))
        chosen_agent_id = candidates[0][2]

        pkg.assigned_agent = chosen_agent_id
        agents[chosen_agent_id].packages_assigned.append(pkg.id)

    return agents