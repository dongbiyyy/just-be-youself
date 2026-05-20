"""Helper to record changes to the audit trail."""
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.change_log import ChangeLog


def _coerce(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def log_change(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    action: str,
    operator: str = "system",
    field: str = "",
    old_value: Any = None,
    new_value: Any = None,
) -> None:
    db.add(
        ChangeLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            field=field,
            old_value=_coerce(old_value),
            new_value=_coerce(new_value),
            operator=operator,
        )
    )


def log_diff(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    operator: str,
    before: dict,
    after: dict,
) -> None:
    """Record every changed field between two snapshots."""
    for key, new_val in after.items():
        old_val = before.get(key)
        if old_val != new_val:
            log_change(
                db,
                entity_type=entity_type,
                entity_id=entity_id,
                action="update",
                operator=operator,
                field=key,
                old_value=old_val,
                new_value=new_val,
            )
