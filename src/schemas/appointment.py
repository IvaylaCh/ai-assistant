from pydantic import BaseModel, Field
from datetime import date, datetime
from models.models import AppointmentStatus


class AvailabilityRequest(BaseModel):
    doctor_id: int
    from_date: date
    to_date: date


class BookRequest(BaseModel):
    doctor_id: int
    patient_name: str
    patient_egn: str = Field(..., min_length=10, max_length=10)
    patient_phone: str
    start_at: datetime


class CancelRequest(BaseModel):
    appointment_id: int


class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_name: str
    patient_egn: str
    patient_phone: str
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    created_at: datetime

    model_config = {"from_attributes": True}
