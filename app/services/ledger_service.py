from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.repositories.customer_repository import CustomerRepository
from app.repositories.ledger_repository import LedgerRepository


class LedgerService:
    def __init__(self, db: Session, customers: CustomerRepository, ledger: LedgerRepository):
        self.db = db
        self.customers = customers
        self.ledger = ledger

    def create_entry(
        self,
        *,
        customer_id: int,
        invoice_id: int,
        entry_type: str,
        amount,
        currency: str,
        reference_id: str,
        description: str,
    ):
        # This service only appends. No update/delete methods are exposed.
        return self.ledger.create(
            {
                "customer_id": customer_id,
                "invoice_id": invoice_id,
                "entry_type": entry_type,
                "amount": amount,
                "currency": currency,
                "reference_id": reference_id,
                "description": description,
            }
        )

    def get_customer_ledger(self, customer_id: int):
        if self.customers.get(customer_id) is None:
            raise NotFoundError("Customer not found.")
        return self.ledger.list_for_customer(customer_id)
