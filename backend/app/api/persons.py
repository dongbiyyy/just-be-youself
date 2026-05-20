from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, hash_id_card
from app.models import Company, Person, Position, Shareholding
from app.schemas import (
    PersonCreate,
    PersonOut,
    PersonUpdate,
    PositionOut,
    ShareholdingOut,
)
from app.services.audit import log_change

router = APIRouter(prefix="/persons", tags=["persons"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[PersonOut])
def list_persons(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    last4: Optional[str] = Query(None, min_length=4, max_length=4),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = db.query(Person)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Person.name.ilike(like), Person.phone.ilike(like), Person.email.ilike(like)))
    if last4:
        query = query.filter(Person.id_card_last4 == last4)
    return query.order_by(Person.id).limit(limit).offset(offset).all()


@router.post("", response_model=PersonOut, status_code=201)
def create_person(payload: PersonCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    h = hash_id_card(payload.id_card)
    if db.query(Person).filter(Person.id_card_hash == h).first():
        raise HTTPException(status_code=400, detail="该身份证号已存在")
    person = Person(
        name=payload.name,
        id_card_hash=h,
        id_card_last4=payload.id_card[-4:],
        nationality=payload.nationality,
        phone=payload.phone,
        email=payload.email,
        gender=payload.gender,
        remark=payload.remark,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    log_change(db, entity_type="person", entity_id=person.id, action="create", operator=user.username, new_value=person.name)
    db.commit()
    return person


@router.get("/{person_id}", response_model=PersonOut)
def get_person(person_id: int, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="人员不存在")
    return p


@router.put("/{person_id}", response_model=PersonOut)
def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="人员不存在")
    data = payload.model_dump(exclude_unset=True)
    if "id_card" in data and data["id_card"]:
        new_card = data.pop("id_card")
        p.id_card_hash = hash_id_card(new_card)
        p.id_card_last4 = new_card[-4:]
    for k, v in data.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    log_change(db, entity_type="person", entity_id=p.id, action="update", operator=user.username)
    db.commit()
    return p


@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="人员不存在")
    log_change(db, entity_type="person", entity_id=p.id, action="delete", operator=user.username, old_value=p.name)
    db.delete(p)
    db.commit()
    return None


@router.get("/{person_id}/positions", response_model=List[PositionOut])
def person_positions(person_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Position, Person, Company)
        .join(Person, Position.person_id == Person.id)
        .join(Company, Position.company_id == Company.id)
        .filter(Position.person_id == person_id)
        .order_by(Position.start_date.desc())
        .all()
    )
    out = []
    for pos, person, comp in rows:
        d = {c.name: getattr(pos, c.name) for c in pos.__table__.columns}
        d["person_name"] = person.name
        d["company_name"] = comp.name
        out.append(d)
    return out


@router.get("/{person_id}/shareholdings", response_model=List[ShareholdingOut])
def person_shareholdings(person_id: int, db: Session = Depends(get_db)):
    rows = db.query(Shareholding).filter(
        Shareholding.shareholder_type == "person",
        Shareholding.shareholder_id == person_id,
    ).all()
    person = db.get(Person, person_id)
    out = []
    for sh in rows:
        d = {c.name: getattr(sh, c.name) for c in sh.__table__.columns}
        d["shareholder_name"] = person.name if person else None
        company = db.get(Company, sh.company_id)
        d["company_name"] = company.name if company else None
        out.append(d)
    return out
