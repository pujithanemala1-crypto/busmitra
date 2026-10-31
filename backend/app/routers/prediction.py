"""
BUSMITRA - Crowd Prediction Router
Endpoints for next-stop passenger density and seat availability forecasting.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.bus_service import resolve_bus
from app.services.prediction_service import prediction_service

router = APIRouter(prefix="", tags=["Crowd Prediction"])

@router.get("/api/buses/{bus_id}/crowd-prediction")
def get_crowd_prediction(bus_id: str, db: Session = Depends(get_db)):
    """
    Returns forecasted crowd level and seat availability when the bus arrives at its approaching stop.
    Integrates real-time onboard load, historical boarding rates, and conductor ETM exit distributions.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    return prediction_service.get_crowd_prediction(db, bus)
