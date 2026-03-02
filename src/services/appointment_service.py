from sqlalchemy.orm import Session
from datetime import date, datetime, time, timedelta
from models.models import Appointment, AppointmentStatus, AvailabilityRule, Doctor


def _slots_for_date(db: Session, doctor_id: int, target_date: date, doctor: Doctor) -> list[datetime]:
    """Returns all free slots for a single day."""
    weekday = target_date.weekday() + 1  # 1=Пон ... 7=Нед

    rule = (
        db.query(AvailabilityRule)
        .filter(
            AvailabilityRule.doctor_id == doctor_id,
            AvailabilityRule.weekday == weekday,
        )
        .first()
    )
    if not rule:
        return []

    slot_duration = timedelta(minutes=doctor.slot_minutes)
    current = datetime.combine(target_date, rule.start_time)
    day_end = datetime.combine(target_date, rule.end_time)

    all_slots = []
    while current + slot_duration <= day_end:
        all_slots.append(current)
        current += slot_duration

    day_start_dt = datetime.combine(target_date, time(0, 0))
    day_end_dt = datetime.combine(target_date, time(23, 59, 59))

    booked = (
        db.query(Appointment.start_at)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.BOOKED,
            Appointment.start_at >= day_start_dt,
            Appointment.start_at <= day_end_dt,
        )
        .all()
    )
    booked_times = {row.start_at for row in booked}

    return [s for s in all_slots if s not in booked_times]


def get_available_slots(
    db: Session,
    doctor_id: int,
    from_date: date,
    to_date: date,
) -> list[datetime]:
    """Returns all free slots for a doctor in [from_date, to_date]."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        return []

    result = []
    current_date = from_date
    while current_date <= to_date:
        result.extend(_slots_for_date(db, doctor_id, current_date, doctor))
        current_date += timedelta(days=1)

    return result


def book_appointment(
    db: Session,
    doctor_id: int,
    patient_name: str,
    patient_egn: str,
    patient_phone: str,
    start_at: datetime,
) -> Appointment:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise ValueError("Лекарят не е намерен.")

    available = _slots_for_date(db, doctor_id, start_at.date(), doctor)
    if start_at not in available:
        raise ValueError("Избраният час не е свободен.")

    end_at = start_at + timedelta(minutes=doctor.slot_minutes)

    appointment = Appointment(
        doctor_id=doctor_id,
        patient_name=patient_name,
        patient_egn=patient_egn,
        patient_phone=patient_phone,
        start_at=start_at,
        end_at=end_at,
        status=AppointmentStatus.BOOKED,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def cancel_appointment(db: Session, appointment_id: int) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise ValueError("Часът не е намерен.")
    if appointment.status == AppointmentStatus.CANCELLED:
        raise ValueError("Часът вече е отменен.")

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointments_by_egn(db: Session, egn: str) -> list[Appointment]:
    return (
        db.query(Appointment)
        .filter(
            Appointment.patient_egn == egn,
            Appointment.status == AppointmentStatus.BOOKED,
        )
        .order_by(Appointment.start_at)
        .all()
    )
