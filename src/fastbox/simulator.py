"""
Delivery route simulation.

ASSUMPTION (documented per assignment instructions):
The brief does not specify the order in which an agent visits their
assigned packages' warehouses/destinations when they have more than one.
Since the brief explicitly says to assume the most efficient reasonable
approach when logic is ambiguous, this module uses a greedy nearest-neighbor
heuristic: starting from the agent's current position, always move to
whichever unvisited leg (a pickup or a drop-off) is closest next. This is
not guaranteed globally optimal (true optimal routing is the Traveling
Salesman Problem, disproportionate effort for this scale), but it is a
clear, deterministic, and reasonable engineering choice.
"""

from typing import Dict, List

from .models import Warehouse, Agent, Package
from .assignment import euclidean_distance


def simulate_deliveries(
    agents: Dict[str, Agent],
    warehouses: Dict[str, Warehouse],
    packages: List[Package],
):
    """
    For each agent, simulate visiting every assigned package: travel to the
    package's warehouse (pickup), then to its destination (drop-off), always
    choosing the nearest unvisited leg next (greedy nearest-neighbor).

    Returns:
        dict[str, dict] keyed by agent id, e.g.:
        {
            "A1": {"packages_delivered": 2, "total_distance": 85.32},
            ...
        }
    """
    packages_by_id = {pkg.id: pkg for pkg in packages}
    results = {}

    for aid, agent in agents.items():
        current_pos = agent.location
        total_distance = 0.0
        delivered = 0

        # Build the list of legs this agent must complete: each assigned
        # package contributes a pickup leg (at its warehouse) and a
        # drop-off leg (at its destination), and drop-off can only happen
        # after that package's pickup.
        remaining_packages = list(agent.packages_assigned)
        pending_pickups = set(remaining_packages)   # package ids not yet picked up
        picked_up = set()                            # package ids picked up, not yet delivered

        # Total legs to visit = 2 per package (pickup + drop-off)
        total_legs = len(remaining_packages) * 2
        visited_legs = 0

        while visited_legs < total_legs:
            # Candidate next stops: warehouse of any pending pickup,
            # or destination of any already-picked-up package.
            candidates = []

            for pkg_id in pending_pickups:
                pkg = packages_by_id[pkg_id]
                wh_loc = warehouses[pkg.warehouse_id].location
                dist = euclidean_distance(current_pos, wh_loc)
                candidates.append((dist, "pickup", pkg_id, wh_loc))

            for pkg_id in picked_up:
                pkg = packages_by_id[pkg_id]
                dist = euclidean_distance(current_pos, pkg.destination)
                candidates.append((dist, "dropoff", pkg_id, pkg.destination))

            # Greedy: pick the nearest candidate leg
            candidates.sort(key=lambda c: (c[0], c[1], c[2]))
            dist, action, pkg_id, next_pos = candidates[0]

            total_distance += dist
            current_pos = next_pos
            visited_legs += 1

            if action == "pickup":
                pending_pickups.remove(pkg_id)
                picked_up.add(pkg_id)
            else:
                picked_up.remove(pkg_id)
                delivered += 1

        results[aid] = {
            "packages_delivered": delivered,
            "total_distance": round(total_distance, 2),
        }

    return results