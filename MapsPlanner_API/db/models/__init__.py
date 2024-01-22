import pkgutil
from pathlib import Path

from MapsPlanner_API.db.models.AuditLog import AuditLogORM
from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM


def load_all_models() -> None:
    """Load all models from this folder."""
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix="MapsPlanner_API.db.models.",
    )
    for module in modules:
        __import__(module.name)  # noqa: WPS421
