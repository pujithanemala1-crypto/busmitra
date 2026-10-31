"""
BUSMITRA - Routes Router
Endpoints for transit corridors, waypoints and stop geometry.
"""
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Route, Stop
from app.schemas import RouteCreate, RouteResponse, StopResponse
from app.routers.users import require_admin_user

router = APIRouter(prefix="", tags=["Routes"])

@router.get("/api/routes")
def get_all_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).all()
    out = []
    for r in routes:
        waypoints = json.loads(r.waypoints_json) if r.waypoints_json else []
        out.append({
            "id": r.id,
            "route_name": r.route_name,
            "source": r.source,
            "destination": r.destination,
            "total_distance": r.total_distance,
            "estimated_duration": r.estimated_duration,
            "waypoints": waypoints,
            "created_at": r.created_at
        })
    return out

@router.get("/api/routes/{route_id}")
def get_route_by_id(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    waypoints = json.loads(route.waypoints_json) if route.waypoints_json else []
    stops = db.query(Stop).filter(Stop.route_id == route.id).order_by(Stop.stop_order.asc()).all()
    return {
        "id": route.id,
        "route_name": route.route_name,
        "source": route.source,
        "destination": route.destination,
        "total_distance": route.total_distance,
        "estimated_duration": route.estimated_duration,
        "waypoints": waypoints,
        "stops": [
            {
                "id": s.id,
                "stop_name": s.stop_name,
                "stop_order": s.stop_order,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "scheduled_arrival_time": s.scheduled_arrival_time
            }
            for s in stops
        ],
        "created_at": route.created_at
    }

@router.get("/api/routes/{route_id}/stops")
def get_route_stops(route_id: int, db: Session = Depends(get_db)):
    stops = db.query(Stop).filter(Stop.route_id == route_id).order_by(Stop.stop_order.asc()).all()
    return [
        {
            "id": s.id,
            "stop_name": s.stop_name,
            "stop_order": s.stop_order,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "scheduled_arrival_time": s.scheduled_arrival_time
        }
        for s in stops
    ]

@router.post("/api/routes", status_code=201)
def create_route(
    route_in: RouteCreate,
    admin=Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    route = Route(
        route_name=route_in.route_name,
        source=route_in.source,
        destination=route_in.destination,
        total_distance=route_in.total_distance,
        estimated_duration=route_in.estimated_duration,
        waypoints_json=route_in.waypoints_json
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    return route
