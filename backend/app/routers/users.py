"""
BUSMITRA - Users, Authentication & ETM Ticketing Router
Handles JWT token generation, admin authentication dependencies, and Conductor ETM records.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from sqlalchemy.orm import Session
from app.database import get_db, hash_password, verify_password
from app.models import (
    User, Bus, Route, Stop, BusLocation, PassengerCount,
    IRSensorEvent, SensorStatus, CrowdPrediction, ETMTicket
)
from app.config import settings
from app.schemas import (
    UserCreate, UserLogin, TokenResponse, UserResponse,
    ETMTicketCreate, ETMTicketResponse, ExpectedExitsResponse
)
from app.services.bus_service import resolve_bus

router = APIRouter(prefix="", tags=["Authentication & ETM"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.username == username).first()
    return user

def require_admin_user(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in with admin credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required for this action."
        )
    return current_user

@router.post("/api/users/login", response_model=TokenResponse)
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }

@router.get("/api/users/me", response_model=UserResponse)
def get_user_profile(user: User = Depends(require_admin_user)):
    return user

@router.get("/api/admin/database-summary")
def get_database_summary(
    user: User = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns record counts for all 10 database tables and SQLite file statistics.
    Accessible only to authenticated administrative users.
    """
    db_path = str(settings.DEFAULT_DB_FILE)
    file_exists = os.path.exists(db_path)
    file_size_bytes = os.path.getsize(db_path) if file_exists else 0

    table_counts = {
        "users": db.query(User).count(),
        "buses": db.query(Bus).count(),
        "routes": db.query(Route).count(),
        "stops": db.query(Stop).count(),
        "bus_locations": db.query(BusLocation).count(),
        "passenger_counts": db.query(PassengerCount).count(),
        "ir_sensor_events": db.query(IRSensorEvent).count(),
        "sensor_status": db.query(SensorStatus).count(),
        "crowd_predictions": db.query(CrowdPrediction).count(),
        "etm_tickets": db.query(ETMTicket).count()
    }

    return {
        "status": "SUCCESS",
        "requested_by": user.username,
        "database_type": "SQLite",
        "database_file": db_path,
        "database_exists": file_exists,
        "database_size_bytes": file_size_bytes,
        "total_records": sum(table_counts.values()),
        "table_counts": table_counts,
        "timestamp": datetime.utcnow()
    }

# --- Conductor ETM (Electronic Ticketing Machine) Endpoints ---

@router.post("/api/etm/tickets", response_model=ETMTicketResponse)
def create_etm_ticket(ticket_in: ETMTicketCreate, db: Session = Depends(get_db)):
    bus = resolve_bus(db, ticket_in.bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    # Check duplicate ticket reference
    existing = db.query(ETMTicket).filter(ETMTicket.ticket_reference == ticket_in.ticket_reference).first()
    if existing:
        return existing

    ticket = ETMTicket(
        bus_id=bus.id,
        boarding_stop_id=ticket_in.boarding_stop_id,
        destination_stop_id=ticket_in.destination_stop_id,
        passenger_count=ticket_in.passenger_count,
        ticket_reference=ticket_in.ticket_reference,
        fare_amount=ticket_in.fare_amount
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/api/buses/{bus_id}/expected-exits", response_model=ExpectedExitsResponse)
def get_expected_exits(bus_id: str, db: Session = Depends(get_db)):
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")

    # Find next approaching stop
    next_stop = None
    if bus.route_id:
        stops = db.query(Stop).filter(Stop.route_id == bus.route_id).order_by(Stop.stop_order.asc()).all()
        if stops:
            target_idx = min(bus.current_stop_index + 1, len(stops) - 1)
            next_stop = stops[target_idx]

    expected_exits = 0
    if next_stop:
        tickets = db.query(ETMTicket).filter(
            ETMTicket.bus_id == bus.id,
            ETMTicket.destination_stop_id == next_stop.id
        ).all()
        expected_exits = sum(t.passenger_count for t in tickets)

    # Actual IR out count for latest stop
    latest_count = (
        db.query(PassengerCount)
        .filter(PassengerCount.bus_id == bus.id)
        .order_by(PassengerCount.recorded_at.desc())
        .first()
    )
    actual_out = latest_count.out_count if latest_count else 0

    mismatch = False
    notes = "ETM tickets and IR sensor outputs are aligned within operational tolerances."
    if expected_exits > 0 and abs(expected_exits - actual_out) > 5:
        mismatch = True
        notes = f"Noticeable variance detected: ETM expected exits ({expected_exits}) vs physical IR alighting pulses ({actual_out})."

    return {
        "bus_id": bus.id,
        "upcoming_stop_id": next_stop.id if next_stop else None,
        "upcoming_stop_name": next_stop.stop_name if next_stop else "Upcoming Stop",
        "expected_exits_etm": expected_exits,
        "actual_ir_out_count": actual_out,
        "mismatch_detected": mismatch,
        "notes": notes
    }
