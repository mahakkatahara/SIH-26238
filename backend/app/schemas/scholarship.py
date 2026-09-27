from typing import Any
from pydantic import BaseModel


class ScholarshipResponse(BaseModel):
    id: str
    code: str
    name: str
    scheme_type: str | None = None
    income_ceiling: int | None = None
    eligible_levels: list[str] | Any | None = None
    is_active: bool = True

    class Config:
        from_attributes = True
