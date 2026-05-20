from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Company, Person, Position, Shareholding
from app.schemas import (
    CompanyCreate,
    CompanyOut,
    CompanyUpdate,
    PositionOut,
    ShareholdingOut,
)
from app.services.audit import log_change, log_diff

router = APIRouter(prefix="/companies", tags=["companies"], dependencies=[Depends(get_current_user)])


def _to_dict(c: Company) -> dict:
    return {
        col.name: getattr(c, col.name) for col in c.__table__.columns
    }


@router.get("", response_model=List[CompanyOut])
def list_companies(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="按名称/信用代码模糊搜索"),
    parent_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = db.query(Company)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Company.name.ilike(like), Company.credit_code.ilike(like)))
    if parent_id is not None:
        query = query.filter(Company.parent_company_id == parent_id)
    return query.order_by(Company.id).limit(limit).offset(offset).all()


@router.post("", response_model=CompanyOut, status_code=201)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if db.query(Company).filter(Company.name == payload.name).first():
        raise HTTPException(status_code=400, detail="公司名称已存在")
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    log_change(
        db,
        entity_type="company",
        entity_id=company.id,
        action="create",
        operator=user.username,
        new_value=company.name,
    )
    db.commit()
    return company


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    c = db.get(Company, company_id)
    if not c:
        raise HTTPException(status_code=404, detail="公司不存在")
    return c


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    c = db.get(Company, company_id)
    if not c:
        raise HTTPException(status_code=404, detail="公司不存在")
    before = _to_dict(c)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    log_diff(
        db,
        entity_type="company",
        entity_id=c.id,
        operator=user.username,
        before=before,
        after=_to_dict(c),
    )
    db.commit()
    return c


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.get(Company, company_id)
    if not c:
        raise HTTPException(status_code=404, detail="公司不存在")
    log_change(
        db,
        entity_type="company",
        entity_id=c.id,
        action="delete",
        operator=user.username,
        old_value=c.name,
    )
    db.delete(c)
    db.commit()
    return None


@router.get("/{company_id}/positions", response_model=List[PositionOut])
def company_positions(company_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Position, Person, Company)
        .join(Person, Position.person_id == Person.id)
        .join(Company, Position.company_id == Company.id)
        .filter(Position.company_id == company_id)
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


@router.get("/{company_id}/shareholdings", response_model=List[ShareholdingOut])
def company_shareholdings(company_id: int, db: Session = Depends(get_db)):
    rows = db.query(Shareholding).filter(Shareholding.company_id == company_id).all()
    enriched = []
    for sh in rows:
        d = {c.name: getattr(sh, c.name) for c in sh.__table__.columns}
        if sh.shareholder_type == "person":
            person = db.get(Person, sh.shareholder_id)
            d["shareholder_name"] = person.name if person else None
        else:
            comp = db.get(Company, sh.shareholder_id)
            d["shareholder_name"] = comp.name if comp else None
        company = db.get(Company, sh.company_id)
        d["company_name"] = company.name if company else None
        enriched.append(d)
    return enriched


@router.get("/{company_id}/tree")
def company_tree(company_id: int, db: Session = Depends(get_db)):
    """Return parent-subsidiary tree rooted at the requested company."""
    root = db.get(Company, company_id)
    if not root:
        raise HTTPException(status_code=404, detail="公司不存在")

    def build(node: Company) -> dict:
        children = db.query(Company).filter(Company.parent_company_id == node.id).all()
        return {
            "id": node.id,
            "name": node.name,
            "credit_code": node.credit_code,
            "children": [build(ch) for ch in children],
        }

    return build(root)
