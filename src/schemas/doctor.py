from pydantic import BaseModel


class DoctorSearchRequest(BaseModel):
    specialty: str | None = None
    location: str | None = None


class DoctorOut(BaseModel):
    id: int
    name: str
    specialty: str
    location: str | None
    slot_minutes: int

    model_config = {"from_attributes": True}
