import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from services.appointment_service import (
    get_available_slots,
    book_appointment,
    cancel_appointment,
    get_appointments_by_egn,
)
from schemas.appointment import AvailabilityRequest, BookRequest, CancelRequest, AppointmentOut

router = APIRouter(tags=["Appointments"])

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


@router.get("/appointments/view", response_class=HTMLResponse, include_in_schema=False)
def appointments_view(request: Request, egn: str | None = None, db: Session = Depends(get_db)):
    appointments = get_appointments_by_egn(db, egn) if egn else []
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "appointments": appointments,
        "egn": egn,
    })


@router.post("/api/availability")
def availability(body: AvailabilityRequest, db: Session = Depends(get_db)):
    slots = get_available_slots(db, body.doctor_id, body.from_date, body.to_date)
    return {"slots": [s.isoformat() for s in slots]}


@router.post("/api/appointments/book", response_model=AppointmentOut, status_code=201)
def book(body: BookRequest, db: Session = Depends(get_db)):
    try:
        return book_appointment(
            db,
            body.doctor_id,
            body.patient_name,
            body.patient_egn,
            body.patient_phone,
            body.start_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/api/appointments/cancel", response_model=AppointmentOut)
def cancel(body: CancelRequest, db: Session = Depends(get_db)):
    try:
        return cancel_appointment(db, body.appointment_id)
    except ValueError as e:
        msg = str(e)
        status_code = 404 if "не е намерен" in msg else 409
        raise HTTPException(status_code=status_code, detail=msg)
