from typing_extensions import TypedDict

TTarget = TypedDict("TTarget", {"model": str, "id": int})
TChanges = TypedDict(
    "TChanges",
    {"before": str | float | int | bool, "after": str | float | int | bool},
)
