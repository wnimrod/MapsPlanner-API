"""MapsPlanner_API package."""

__version__ = "0.0.3"

from enum import Enum


class Environment(Enum):
    Local = "local"
    Pytest = "pytest"
    Testing = "testing"
    Production = "production"
