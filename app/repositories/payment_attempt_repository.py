from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PaymentAttempt


class PaymentAttemptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> PaymentAttempt:
        attempt = PaymentAttempt(**data)
        self.db.add(attempt)
        self.db.flush()
        return attempt

    def list_for_invoice(self, invoice_id: int) -> list[PaymentAttempt]:
        return list(
            self.db.scalars(
                select(PaymentAttempt)
                .where(PaymentAttempt.invoice_id == invoice_id)
                .order_by(PaymentAttempt.id)
            ).all()
        )
