"""Conflict detection engine.

Scans current (un-ended) Position rows and raises Alerts when configured rules match.
"""
from datetime import date
from typing import Iterable, List

from sqlalchemy.orm import Session

from app.models import Alert, Company, ConflictRule, Person, Position
from app.models.alert import AlertStatus


# Default rules seeded on first run.
DEFAULT_RULES = [
    {
        "name": "监事不得兼任董事",
        "rule_type": "incompatible_positions",
        "position_a": "监事",
        "position_b": "董事",
        "scope": "any",
        "severity": "critical",
        "description": "根据《公司法》第五十一条，监事不得兼任董事或高级管理人员。",
    },
    {
        "name": "监事不得兼任高管",
        "rule_type": "incompatible_positions",
        "position_a": "监事",
        "position_b": "总经理",
        "scope": "any",
        "severity": "critical",
        "description": "根据《公司法》第五十一条，监事不得兼任高级管理人员。",
    },
    {
        "name": "母子公司同任董事提示",
        "rule_type": "incompatible_positions",
        "position_a": "董事",
        "position_b": "董事",
        "scope": "parent_subsidiary",
        "severity": "warning",
        "description": "同一人在母子公司同时担任董事，建议复核以防关联交易风险。",
    },
]


def ensure_default_rules(db: Session) -> None:
    if db.query(ConflictRule).count() == 0:
        for r in DEFAULT_RULES:
            db.add(ConflictRule(**r))
        db.commit()


def _active(p: Position) -> bool:
    return p.end_date is None or p.end_date >= date.today()


def _is_parent_subsidiary(a: Company, b: Company) -> bool:
    if a is None or b is None or a.id == b.id:
        return False
    return a.parent_company_id == b.id or b.parent_company_id == a.id


def detect_conflicts(db: Session) -> List[Alert]:
    """Run all enabled rules and write new open Alerts for any matches not yet recorded."""
    ensure_default_rules(db)
    rules = db.query(ConflictRule).filter(ConflictRule.enabled.is_(True)).all()

    # Build lookup: person_id -> [(position, company)]
    positions = (
        db.query(Position, Company)
        .join(Company, Position.company_id == Company.id)
        .all()
    )
    by_person: dict[int, list[tuple[Position, Company]]] = {}
    for pos, comp in positions:
        if _active(pos):
            by_person.setdefault(pos.person_id, []).append((pos, comp))

    existing_titles = {
        a.title for a in db.query(Alert).filter(Alert.kind == "conflict", Alert.status == AlertStatus.OPEN.value)
    }
    new_alerts: List[Alert] = []

    for person_id, items in by_person.items():
        person = db.get(Person, person_id)
        if not person:
            continue
        for rule in rules:
            for i in range(len(items)):
                for j in range(len(items)):
                    if i == j and rule.position_a == rule.position_b:
                        continue
                    pos_a, comp_a = items[i]
                    pos_b, comp_b = items[j]
                    if pos_a.position_type != rule.position_a:
                        continue
                    if pos_b.position_type != rule.position_b:
                        continue
                    if rule.scope == "same_company" and comp_a.id != comp_b.id:
                        continue
                    if rule.scope == "parent_subsidiary" and not _is_parent_subsidiary(comp_a, comp_b):
                        continue
                    if rule.scope == "any" and comp_a.id == comp_b.id and pos_a.id == pos_b.id:
                        continue
                    title = (
                        f"[{rule.name}] {person.name} 同时在 {comp_a.name} 任{rule.position_a}"
                        f"，在 {comp_b.name} 任{rule.position_b}"
                    )
                    if title in existing_titles:
                        continue
                    alert = Alert(
                        kind="conflict",
                        severity=rule.severity,
                        title=title,
                        detail=rule.description,
                        related_entity_type="person",
                        related_entity_id=person.id,
                    )
                    db.add(alert)
                    new_alerts.append(alert)
                    existing_titles.add(title)
    if new_alerts:
        db.commit()
    return new_alerts


def detect_term_expiry(db: Session, *, warn_days: Iterable[int] = (30, 60, 90)) -> List[Alert]:
    """Generate reminders for positions whose end_date falls within warn_days."""
    today = date.today()
    max_window = max(warn_days)
    rows = (
        db.query(Position, Person, Company)
        .join(Person, Position.person_id == Person.id)
        .join(Company, Position.company_id == Company.id)
        .filter(Position.end_date.isnot(None))
        .all()
    )
    existing = {
        a.title for a in db.query(Alert).filter(Alert.kind == "term_expiry", Alert.status == AlertStatus.OPEN.value)
    }
    new_alerts: List[Alert] = []
    for pos, person, comp in rows:
        if pos.end_date is None:
            continue
        delta = (pos.end_date - today).days
        if delta < 0 or delta > max_window:
            continue
        bucket = min(d for d in warn_days if delta <= d)
        title = f"任期提醒：{person.name} 在 {comp.name} 的 {pos.position_type} 任期将于 {pos.end_date} 到期（{bucket} 天内）"
        if title in existing:
            continue
        alert = Alert(
            kind="term_expiry",
            severity="warning" if bucket > 30 else "critical",
            title=title,
            detail=f"职务文号: {pos.document_no or '-'}",
            related_entity_type="position",
            related_entity_id=pos.id,
        )
        db.add(alert)
        new_alerts.append(alert)
        existing.add(title)
    if new_alerts:
        db.commit()
    return new_alerts
