"""
Data models for the FastBox delivery simulation.

Using simple dataclasses keeps warehouses, agents, and packages as clean,
typed objects instead of raw dicts — everything downstream (assignment,
simulation, reporting) operates on these, regardless of which JSON schema
the input file originally used.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Warehouse:
    id: str
    location: Tuple[float, float]


@dataclass
class Agent:
    id: str
    location: Tuple[float, float]
    packages_assigned: List[str] = field(default_factory=list)


@dataclass
class Package:
    id: str
    warehouse_id: str
    destination: Tuple[float, float]
    assigned_agent: str = None