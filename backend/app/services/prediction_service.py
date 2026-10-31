"""
BUSMITRA - Next Stop Crowd Prediction Service
Combines current occupancy, historical boarding averages, and ETM alighting distributions
to forecast crowd density at approaching bus stops.
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Bus, Stop, CrowdPrediction, PassengerCount, ETMTicket
from app.utils.calculations import calculate_occupancy_metrics

class PredictionService:
    @staticmethod
    def get_crowd_prediction(db: Session, bus: Bus) -> Dict[str, Any]:
        # 1. Fetch Latest Passenger Count
        latest_count = (
            db.query(PassengerCount)
            .filter(PassengerCount.bus_id == bus.id)
            .order_by(PassengerCount.recorded_at.desc(), PassengerCount.id.desc())
            .first()
        )
        current_passengers = latest_count.current_passengers if latest_count else 0
        current_occ = (
            round((current_passengers / bus.capacity) * 100.0, 1)
            if bus.capacity > 0
            else 0.0
        )

        # 2. Identify Next Stop on Route
        next_stop = None
        if bus.route_id:
            stops = (
                db.query(Stop)
                .filter(Stop.route_id == bus.route_id)
                .order_by(Stop.stop_order.asc())
                .all()
            )
            # Find next approaching stop
            if stops:
                target_idx = min(bus.current_stop_index + 1, len(stops) - 1)
                next_stop = stops[target_idx]

        next_stop_name = next_stop.stop_name if next_stop else "Approaching Stop"

        # 3. ETM Expected Exits lookup
        etm_exits = 0
        if next_stop:
            etm_tickets = (
                db.query(ETMTicket)
                .filter(
                    ETMTicket.bus_id == bus.id,
                    ETMTicket.destination_stop_id == next_stop.id
                )
                .all()
            )
            etm_exits = sum(t.passenger_count for t in etm_tickets)

        # 4. Check Stored Historical Prediction
        stored_pred = (
            db.query(CrowdPrediction)
            .filter(CrowdPrediction.bus_id == bus.id)
            .order_by(CrowdPrediction.created_at.desc())
            .first()
        )

        if stored_pred:
            expected_boarding = stored_pred.expected_boarding
            # Combine ETM exits with historical alighting
            expected_exiting = max(stored_pred.expected_exiting, etm_exits)
            confidence = stored_pred.confidence
            pred_source = stored_pred.prediction_source
        else:
            # Fallback heuristic if no history
            expected_boarding = 6
            expected_exiting = max(3, etm_exits)
            confidence = "85%"
            pred_source = "Stop Average Heuristics (SIMULATED)"

        # Cap alighting so it does not exceed current onboard passengers
        actual_expected_exit = min(current_passengers, expected_exiting)
        predicted_passengers = max(0, current_passengers + expected_boarding - actual_expected_exit)
        predicted_seats = max(0, bus.capacity - predicted_passengers)
        predicted_occ = round((predicted_passengers / bus.capacity) * 100.0, 1)

        if predicted_occ <= 40.0:
            pred_level = "LOW"
        elif predicted_occ <= 75.0:
            pred_level = "MODERATE"
        elif predicted_occ <= 100.0:
            pred_level = "HIGH"
        else:
            pred_level = "OVERCROWDED"

        return {
            "bus_id": bus.id,
            "busId": bus.id,
            "bus_number": bus.bus_number,
            "next_stop": next_stop_name,
            "nextStop": next_stop_name,
            "current_occupancy": f"{current_occ}%",
            "currentOccupancy": f"{current_occ}%",
            "predicted_occupancy": predicted_occ,
            "predictedOccupancy": predicted_occ,
            "predicted_occupancy_formatted": f"{predicted_occ}%",
            "expected_boarding": expected_boarding,
            "expectedBoarding": expected_boarding,
            "expected_exiting": actual_expected_exit,
            "expectedAlighting": actual_expected_exit,
            "predicted_available_seats": predicted_seats,
            "predictedAvailableSeats": predicted_seats,
            "predicted_crowd_level": pred_level,
            "predictedCrowdLevel": pred_level,
            "prediction_confidence": confidence,
            "confidence": confidence,
            "prediction_source": pred_source,
            "dataSource": pred_source,
            "is_simulated": True,
            "generated_at": datetime.utcnow()
        }

prediction_service = PredictionService()
