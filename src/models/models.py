from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Time
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from database import Base


class AppointmentStatus(str, enum.Enum):
    BOOKED = "ЗАПИСАН"
    CANCELLED = "ОТМЕНЕН"
    COMPLETED = "ЗАВЪРШЕН"


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    location = Column(String(200), nullable=True)
    slot_minutes = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)

    availability_rules = relationship("AvailabilityRule", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")


class AvailabilityRule(Base):
    __tablename__ = "availability_rules"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    weekday = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    doctor = relationship("Doctor", back_populates="availability_rules")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_egn = Column(String(10), nullable=False, index=True)
    patient_phone = Column(String(20), nullable=False, index=True)
    patient_name = Column(String(100), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus, values_callable=lambda x: [e.value for e in x]), default=AppointmentStatus.BOOKED)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    doctor = relationship("Doctor", back_populates="appointments")
