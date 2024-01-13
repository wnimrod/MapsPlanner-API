from typing import Any, TypedDict

TTarget = TypedDict("TTarget", {"model": str, "id": int})
TChanges = TypedDict("TChanges", {"before": Any, "after": Any})
