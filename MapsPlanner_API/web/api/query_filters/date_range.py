from datetime import datetime, timezone
from typing import Optional, Annotated

import dateutil.parser
from fastapi.params import Query
from pydantic import AfterValidator


def date_range_param_validator(
    date_range: str,
) -> [Optional[datetime], Optional[datetime]]:
    try:
        start, end = date_range.split("...")
        date_range = []
        for timestr in [start, end]:
            if not timestr:
                date_range.append(None)
                continue
            try:
                date_range.append(dateutil.parser.parse(timestr))
            except ValueError:
                date_range.append(
                    datetime.fromtimestamp(float(timestr), tz=timezone.utc)
                )
        return date_range
    except ValueError as err:
        raise ValueError("Invalid format for date range field.") from err


def DateRangeFilter(description="", examples=None):
    return Annotated[
        str,
        AfterValidator(date_range_param_validator),
        Query(
            description=description,
            examples=examples,
        ),
    ]
