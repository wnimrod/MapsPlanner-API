from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DateRangeFilter(BaseModel):
    start: Optional[datetime]
    end: Optional[datetime]
