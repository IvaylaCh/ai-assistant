from sqlalchemy.orm import Session
from models.models import Doctor


def get_all_doctors(db: Session) -> list[Doctor]:
    return db.query(Doctor).filter(Doctor.is_active == True).all()


def get_doctor_by_id(db: Session, doctor_id: int) -> Doctor | None:
    return db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.is_active == True).first()


def get_doctors_by_specialty(db: Session, specialty: str) -> list[Doctor]:
    return (
        db.query(Doctor)
        .filter(Doctor.specialty.ilike(f"%{specialty}%"), Doctor.is_active == True)
        .all()
    )


def search_doctors(db: Session, specialty: str | None, location: str | None) -> list[Doctor]:
    q = db.query(Doctor).filter(Doctor.is_active == True)
    if specialty:
        q = q.filter(Doctor.specialty.ilike(f"%{specialty}%"))
    if location:
        q = q.filter(Doctor.location.ilike(f"%{location}%"))
    return q.all()
