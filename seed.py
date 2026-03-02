from database import SessionLocal
from src.models.models import Doctor, AvailabilityRule
from datetime import time

def seed():
    db = SessionLocal()
    
    if db.query(Doctor).count() > 0:
        print("Базата вече има данни, пропускам seed.")
        db.close()
        return

    print("Добавям тестови лекари...")

    doctors = [
        Doctor(name="Д-р Иван Петров", specialty="кардиолог", 
               location="София - Център", slot_minutes=30),
        Doctor(name="Д-р Мария Иванова", specialty="дерматолог", 
               location="София - Юг", slot_minutes=20),
        Doctor(name="Д-р Георги Димитров", specialty="ортопед", 
               location="Пловдив", slot_minutes=45),
    ]
    
    db.add_all(doctors)
    db.flush()

    # Д-р Петров - Пон-Пет, 9:00-17:00
    for weekday in range(1, 6):
        db.add(AvailabilityRule(
            doctor_id=doctors[0].id,
            weekday=weekday,
            start_time=time(9, 0),
            end_time=time(17, 0)
        ))

    # Д-р Иванова - Пон/Сря/Пет, 10:00-15:00
    for weekday in [1, 3, 5]:
        db.add(AvailabilityRule(
            doctor_id=doctors[1].id,
            weekday=weekday,
            start_time=time(10, 0),
            end_time=time(15, 0)
        ))

    # Д-р Димитров - Вт/Чет, 8:00-14:00
    for weekday in [2, 4]:
        db.add(AvailabilityRule(
            doctor_id=doctors[2].id,
            weekday=weekday,
            start_time=time(8, 0),
            end_time=time(14, 0)
        ))

    db.commit()
    print(f"✅ Добавени {len(doctors)} лекари с разписания!")
    db.close()

if __name__ == "__main__":
    seed()