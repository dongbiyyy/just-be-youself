from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Company, Person
from app.schemas import SearchHit

router = APIRouter(prefix="/search", tags=["search"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[SearchHit])
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db), limit: int = 30):
    """Full-text style search across companies and persons.

    Matches by company name / credit code / short name / legal representative,
    and by person name / phone / email / id_card_last4.
    """
    like = f"%{q}%"
    out: List[SearchHit] = []
    for c in (
        db.query(Company)
        .filter(
            or_(
                Company.name.ilike(like),
                Company.credit_code.ilike(like),
                Company.short_name.ilike(like),
                Company.legal_representative.ilike(like),
            )
        )
        .limit(limit)
        .all()
    ):
        out.append(SearchHit(type="company", id=c.id, name=c.name, extra=c.credit_code or ""))

    person_filters = [
        Person.name.ilike(like),
        Person.phone.ilike(like),
        Person.email.ilike(like),
    ]
    if len(q) == 4 and q.isdigit():
        person_filters.append(Person.id_card_last4 == q)
    person_query = db.query(Person).filter(or_(*person_filters))
    for p in person_query.limit(limit).all():
        out.append(SearchHit(type="person", id=p.id, name=p.name, extra=f"尾号{p.id_card_last4}"))
    return out
