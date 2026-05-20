from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Company, Person, Shareholding
from app.schemas import ShareholdingCreate, ShareholdingOut
from app.services.audit import log_change

router = APIRouter(prefix="/shareholdings", tags=["shareholdings"], dependencies=[Depends(get_current_user)])


def _enrich(sh: Shareholding, db: Session) -> dict:
    d = {c.name: getattr(sh, c.name) for c in sh.__table__.columns}
    if sh.shareholder_type == "person":
        person = db.get(Person, sh.shareholder_id)
        d["shareholder_name"] = person.name if person else None
    else:
        comp = db.get(Company, sh.shareholder_id)
        d["shareholder_name"] = comp.name if comp else None
    company = db.get(Company, sh.company_id)
    d["company_name"] = company.name if company else None
    return d


@router.get("", response_model=List[ShareholdingOut])
def list_shareholdings(
    db: Session = Depends(get_db),
    company_id: Optional[int] = None,
    shareholder_type: Optional[str] = None,
    shareholder_id: Optional[int] = None,
    limit: int = Query(200, ge=1, le=1000),
):
    q = db.query(Shareholding)
    if company_id:
        q = q.filter(Shareholding.company_id == company_id)
    if shareholder_type:
        q = q.filter(Shareholding.shareholder_type == shareholder_type)
    if shareholder_id:
        q = q.filter(Shareholding.shareholder_id == shareholder_id)
    return [_enrich(sh, db) for sh in q.limit(limit).all()]


@router.post("", response_model=ShareholdingOut, status_code=201)
def create_shareholding(payload: ShareholdingCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if payload.shareholder_type not in ("person", "company"):
        raise HTTPException(status_code=400, detail="shareholder_type 必须是 person 或 company")
    if not db.get(Company, payload.company_id):
        raise HTTPException(status_code=400, detail="公司不存在")
    if payload.shareholder_type == "person":
        if not db.get(Person, payload.shareholder_id):
            raise HTTPException(status_code=400, detail="股东(人)不存在")
    else:
        if not db.get(Company, payload.shareholder_id):
            raise HTTPException(status_code=400, detail="股东(公司)不存在")
    sh = Shareholding(**payload.model_dump())
    db.add(sh)
    db.commit()
    db.refresh(sh)
    log_change(db, entity_type="shareholding", entity_id=sh.id, action="create", operator=user.username)
    db.commit()
    return _enrich(sh, db)


@router.delete("/{shareholding_id}", status_code=204)
def delete_shareholding(shareholding_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sh = db.get(Shareholding, shareholding_id)
    if not sh:
        raise HTTPException(status_code=404, detail="持股记录不存在")
    log_change(db, entity_type="shareholding", entity_id=sh.id, action="delete", operator=user.username)
    db.delete(sh)
    db.commit()
    return None
