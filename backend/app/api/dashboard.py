from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Alert, ChangeLog, Company, Person, Position, Shareholding
from app.schemas import AlertOut
from app.services.conflict import detect_conflicts, detect_term_expiry

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return {
        "companies": db.query(Company).count(),
        "persons": db.query(Person).count(),
        "positions": db.query(Position).count(),
        "shareholdings": db.query(Shareholding).count(),
        "open_alerts": db.query(Alert).filter(Alert.status == "open").count(),
    }


@router.get("/alerts", response_model=List[AlertOut])
def alerts(
    db: Session = Depends(get_db),
    status: str = Query("open"),
    limit: int = Query(100, ge=1, le=500),
):
    return (
        db.query(Alert)
        .filter(Alert.status == status)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/alerts/recompute")
def recompute_alerts(db: Session = Depends(get_db)):
    conflicts = detect_conflicts(db)
    expiries = detect_term_expiry(db)
    return {"new_conflicts": len(conflicts), "new_term_expiries": len(expiries)}


@router.get("/recent-changes")
def recent_changes(db: Session = Depends(get_db), limit: int = Query(30, ge=1, le=200)):
    rows = db.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "action": r.action,
            "field": r.field,
            "old_value": r.old_value,
            "new_value": r.new_value,
            "operator": r.operator,
            "timestamp": r.timestamp,
        }
        for r in rows
    ]
