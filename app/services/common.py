"""Shared database transaction helper used by write services."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError


def commit_changes(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A record with conflicting unique values already exists.") from exc
    except Exception:
        db.rollback()
        raise
