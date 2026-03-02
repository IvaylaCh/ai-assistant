from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.doctor_service import get_doctor_by_id, search_doctors
from schemas.doctor import DoctorOut, DoctorSearchRequest

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


@router.post("/search", response_model=list[DoctorOut])
def search(body: DoctorSearchRequest, db: Session = Depends(get_db)):
    return search_doctors(db, body.specialty, body.location)


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Лекарят не е намерен.")
    return doctor
