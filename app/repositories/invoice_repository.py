from sqlalchemy.orm import Session

from app.models import Invoice


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Invoice:
        invoice = Invoice(**data)
        self.db.add(invoice)
        self.db.flush()
        return invoice

    def get(self, invoice_id: int) -> Invoice | None:
        return self.db.get(Invoice, invoice_id)
