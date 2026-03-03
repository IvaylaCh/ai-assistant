import sys
import os

_src_dir = os.path.dirname(os.path.abspath(__file__))          # .../src
_project_root = os.path.dirname(_src_dir)                       # .../ai-assistant

# src/ — so that 'from routes.x import ...' etc. resolve correctly
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)
# project root — so that 'from database import ...' resolves correctly
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI
from routes.doctors import router as doctors_router
from routes.appointments import router as appointments_router
from routes.vapi import router as vapi_router

app = FastAPI(title="AI Телефонен Рецепционист")

app.include_router(doctors_router)
app.include_router(appointments_router)
app.include_router(vapi_router)


@app.get("/health")
def health():
    return {"status": "ok"}
