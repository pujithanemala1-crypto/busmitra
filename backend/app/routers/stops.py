"""
BUSMITRA - Stops Router
Endpoints for managing transit stops and boarding locations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stop, Route
from app.schemas import StopCreate, StopResponse
from app.routers.users import require_admin_user

router = APIRouter(prefix="", tags=["Stops"])

@router.get("/api/stops", response_model=List[StopResponse])
def get_all_stops(db: Session = Depends(get_db)):
    return db.query(Stop).order_by(Stop.route_id.asc(), Stop.stop_order.asc()).all()

@router.post("/api/stops", response_model=StopResponse, status_code=201)
def create_stop(
    stop_in: StopCreate,
    admin=Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    route = db.query(Route).filter(Route.id == stop_in.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Associated route not found")

    stop = Stop(
        route_id=stop_in.route_id,
        stop_name=stop_in.stop_name,
        stop_order=stop_in.stop_order,
        latitude=stop_in.latitude,
        longitude=stop_in.longitude,
        scheduled_arrival_time=stop_in.scheduled_arrival_time
    )
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return stop
