import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from services.doctor_service import search_doctors
from services.appointment_service import (
    get_available_slots,
    book_appointment,
    cancel_appointment,
)

router = APIRouter(prefix="/vapi", tags=["Vapi"])


def _handle_tool(name: str, args: dict, db: Session) -> str:
    """Dispatch a Vapi tool call and return a human-readable string result."""

    if name == "search_doctors":
        specialty = args.get("specialty")
        location = args.get("location")
        doctors = search_doctors(db, specialty, location)
        if not doctors:
            return "Не намерих лекари по тези критерии."
        lines = [f"ID {d.id}: {d.name} — {d.specialty}, {d.location or 'неизвестно'}" for d in doctors]
        return "Намерени лекари:\n" + "\n".join(lines)

    elif name == "get_available_slots":
        doctor_id = int(args["doctor_id"])
        from_date = date.fromisoformat(args["from_date"])
        to_date = date.fromisoformat(args["to_date"])
        slots = get_available_slots(db, doctor_id, from_date, to_date)
        if not slots:
            return "Няма свободни часове в избрания период."
        lines = [s.strftime("%d.%m.%Y %H:%M") for s in slots[:20]]  # max 20 за четимост
        suffix = f"\n(и още {len(slots) - 20})" if len(slots) > 20 else ""
        return "Свободни часове:\n" + "\n".join(lines) + suffix

    elif name == "book_appointment":
        doctor_id = int(args["doctor_id"])
        patient_name = args["patient_name"]
        patient_egn = args["patient_egn"]
        patient_phone = args["patient_phone"]
        start_at = datetime.fromisoformat(args["start_at"])
        try:
            appt = book_appointment(db, doctor_id, patient_name, patient_egn, patient_phone, start_at)
            return (
                f"Успешно записан час №{appt.id} за {appt.patient_name} "
                f"на {appt.start_at.strftime('%d.%m.%Y %H:%M')} — {appt.end_at.strftime('%H:%M')}."
            )
        except ValueError as e:
            return f"Грешка: {e}"

    elif name == "cancel_appointment":
        appointment_id = int(args["appointment_id"])
        try:
            appt = cancel_appointment(db, appointment_id)
            return (
                f"Час №{appt.id} за {appt.patient_name} на "
                f"{appt.start_at.strftime('%d.%m.%Y %H:%M')} беше успешно отменен."
            )
        except ValueError as e:
            return f"Грешка: {e}"

    return f"Непознат инструмент: {name}"


@router.post("/webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    message = body.get("message", {})
    msg_type = message.get("type")

    if msg_type == "tool-calls":
        results = []
        for tool_call in message.get("toolCallList", []):
            tool_id = tool_call.get("id", "")
            func = tool_call.get("function", {})
            name = func.get("name", "")
            raw_args = func.get("arguments", "{}")
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

            result = _handle_tool(name, args, db)
            results.append({"toolCallId": tool_id, "result": result})

        return {"results": results}

    # Vapi изпраща и други типове (start, end, transcript) — просто ги игнорираме
    return {}
