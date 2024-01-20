from datetime import datetime, timezone
from typing_extensions import Optional, Annotated, Self

import dateutil.parser
from fastapi.params import Query
from pydantic import AfterValidator, field_validator, model_validator


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


class DateRangeFilterMixin:
    # TODO: Add the ability to give other name than `creation_date`
    creation_range: Optional[str] = None

    # Dynamically generated
    creation_date__gte: Optional[datetime] = None
    creation_date__lte: Optional[datetime] = None

    @field_validator("creation_range", mode="after")
    def validate_creation_range(cls, creation_range):
        return date_range_param_validator(creation_range)

    @model_validator(mode="after")
    def validate(self) -> Self:
        self.creation_date__gte, self.creation_date__lte = self.creation_range or (
            None,
            None,
        )
        del self.creation_range
        return self


def DateRangeFilter(description="", examples=None):
    return Annotated[
        str,
        AfterValidator(date_range_param_validator),
        Query(
            description=description,
            examples=examples,
        ),
    ]
