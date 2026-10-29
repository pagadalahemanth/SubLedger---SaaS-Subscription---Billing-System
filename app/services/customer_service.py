from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.repositories.customer_repository import CustomerRepository
from app.schemas import CustomerCreate
from app.services.common import commit_changes


class CustomerService:
    def __init__(self, db: Session, repository: CustomerRepository):
        self.db = db
        self.repository = repository

    def create_customer(self, payload: CustomerCreate):
        email = str(payload.email).strip().lower()
        if self.repository.get_by_email(email) is not None:
            raise ConflictError("A customer with this email already exists.")

        customer = self.repository.create(
            {
                "name": payload.name.strip(),
                "email": email,
                "company_name": payload.company_name,
            }
        )
        commit_changes(self.db)
        self.db.refresh(customer)
        return customer

    def list_customers(self):
        return self.repository.list_all()

    def get_customer(self, customer_id: int):
        customer = self.repository.get(customer_id)
        if customer is None:
            raise NotFoundError("Customer not found.")
        return customer
