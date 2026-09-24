"""
Schema-agnostic JSON loader for the FastBox delivery simulation.

ASSUMPTION (documented per assignment instructions):
The provided test data does not use one consistent schema. Two shapes appear:

  Shape A (dict-keyed) — e.g. the PDF's example data.json, test_case_1..10.json
      "warehouses": {"W1": [0, 0], ...}
      "agents":     {"A1": [5, 5], ...}
      "packages":   [{"id": "P1", "warehouse": "W1", "destination": [30, 40]}]

  Shape B (list-of-objects) — e.g. base_case.json
      "warehouses": [{"id": "W1", "location": [0, 0]}, ...]
      "agents":     [{"id": "A1", "location": [5, 5]}, ...]
      "packages":   [{"id": "P1", "warehouse_id": "W1", "destination": [30, 40]}]

Rather than assume one schema (which would crash on the other set of files),
this loader detects the shape of each top-level section independently and
normalizes everything into the same internal dataclasses (Warehouse, Agent,
Package) before any other module ever sees the data.
"""

import json
from typing import Dict

from .models import Warehouse, Agent, Package


def _normalize_points(section, id_key="id", loc_key="location"):
    """
    Normalize a 'warehouses' or 'agents' section into {id: (x, y)}.
    Handles both dict shape ({"W1": [0,0]}) and list shape
    ([{"id": "W1", "location": [0,0]}]).
    """
    normalized: Dict[str, tuple] = {}

    if isinstance(section, dict):
        for point_id, coords in section.items():
            normalized[point_id] = (float(coords[0]), float(coords[1]))

    elif isinstance(section, list):
        for entry in section:
            point_id = entry[id_key]
            coords = entry[loc_key]
            normalized[point_id] = (float(coords[0]), float(coords[1]))

    else:
        raise ValueError(
            f"Unrecognized schema: expected dict or list, got {type(section)}"
        )

    return normalized


def _normalize_packages(section):
    """
    Normalize the 'packages' list. Handles both the 'warehouse' key
    (dict-shape files) and 'warehouse_id' key (base_case.json).
    """
    packages = []
    for entry in section:
        warehouse_ref = entry.get("warehouse", entry.get("warehouse_id"))
        if warehouse_ref is None:
            raise ValueError(
                f"Package {entry.get('id', '?')} has no 'warehouse' or "
                f"'warehouse_id' field — cannot determine pickup location."
            )
        dest = entry["destination"]
        packages.append(Package(
            id=entry["id"],
            warehouse_id=warehouse_ref,
            destination=(float(dest[0]), float(dest[1])),
        ))
    return packages


def load_data(path: str):
    """
    Load and normalize a FastBox input JSON file, regardless of which of
    the two known schema shapes it uses.

    Returns:
        (warehouses, agents, packages)
        warehouses: dict[str, Warehouse]
        agents:     dict[str, Agent]
        packages:   list[Package]
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    for required in ("warehouses", "agents", "packages"):
        if required not in raw:
            raise ValueError(f"Input file is missing required section: '{required}'")

    warehouse_points = _normalize_points(raw["warehouses"])
    agent_points = _normalize_points(raw["agents"])

    warehouses = {wid: Warehouse(id=wid, location=loc) for wid, loc in warehouse_points.items()}
    agents = {aid: Agent(id=aid, location=loc) for aid, loc in agent_points.items()}
    packages = _normalize_packages(raw["packages"])

    for pkg in packages:
        if pkg.warehouse_id not in warehouses:
            raise ValueError(
                f"Package {pkg.id} references unknown warehouse '{pkg.warehouse_id}'"
            )

    return warehouses, agents, packages