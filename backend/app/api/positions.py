from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Company, Person, Position
from app.schemas import PositionCreate, PositionOut, PositionUpdate
from app.services.audit import log_change

router = APIRouter(prefix="/positions", tags=["positions"], dependencies=[Depends(get_current_user)])


def _enrich(pos: Position, db: Session) -> dict:
    d = {c.name: getattr(pos, c.name) for c in pos.__table__.columns}
    person = db.get(Person, pos.person_id)
    company = db.get(Company, pos.company_id)
    d["person_name"] = person.name if person else None
    d["company_name"] = company.name if company else None
    return d


@router.get("", response_model=List[PositionOut])
def list_positions(
    db: Session = Depends(get_db),
    company_id: Optional[int] = None,
    person_id: Optional[int] = None,
    active_only: bool = False,
    limit: int = Query(200, ge=1, le=1000),
):
    q = db.query(Position)
    if company_id:
        q = q.filter(Position.company_id == company_id)
    if person_id:
        q = q.filter(Position.person_id == person_id)
    if active_only:
        from datetime import date
        q = q.filter((Position.end_date.is_(None)) | (Position.end_date >= date.today()))
    return [_enrich(p, db) for p in q.order_by(Position.start_date.desc()).limit(limit).all()]


@router.post("", response_model=PositionOut, status_code=201)
def create_position(payload: PositionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not db.get(Person, payload.person_id):
        raise HTTPException(status_code=400, detail="人员不存在")
    if not db.get(Company, payload.company_id):
        raise HTTPException(status_code=400, detail="公司不存在")
    pos = Position(**payload.model_dump())
    db.add(pos)
    db.commit()
    db.refresh(pos)
    log_change(db, entity_type="position", entity_id=pos.id, action="create", operator=user.username,
               new_value=f"{payload.position_type}@{payload.company_id}")
    db.commit()
    return _enrich(pos, db)


@router.put("/{position_id}", response_model=PositionOut)
def update_position(position_id: int, payload: PositionUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pos = db.get(Position, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="任职记录不存在")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(pos, k, v)
    db.commit()
    db.refresh(pos)
    log_change(db, entity_type="position", entity_id=pos.id, action="update", operator=user.username)
    db.commit()
    return _enrich(pos, db)


@router.delete("/{position_id}", status_code=204)
def delete_position(position_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pos = db.get(Position, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="任职记录不存在")
    log_change(db, entity_type="position", entity_id=pos.id, action="delete", operator=user.username)
    db.delete(pos)
    db.commit()
    return None
