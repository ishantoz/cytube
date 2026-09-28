from pydantic import BaseModel, Field


class InspectRequest(BaseModel):
    url: str = ""


class JobRequest(BaseModel):
    url: str
    format_id: str
    kind: str
    label: str = Field(default="")
