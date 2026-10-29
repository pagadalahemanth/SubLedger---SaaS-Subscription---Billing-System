from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LedgerEntry


class LedgerRepository:
    """Ledger entries can be created and read; there are no update/delete methods."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> LedgerEntry:
        entry = LedgerEntry(**data)
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_for_customer(self, customer_id: int) -> list[LedgerEntry]:
        return list(
            self.db.scalars(
                select(LedgerEntry)
                .where(LedgerEntry.customer_id == customer_id)
                .order_by(LedgerEntry.created_at, LedgerEntry.id)
            ).all()
        )
