from pydantic import BaseModel


class Track(BaseModel):
    id: int
    name: str
    volume: float = 1.0
    muted: bool = False
    solo: bool = False
    rec_armed: bool = False
