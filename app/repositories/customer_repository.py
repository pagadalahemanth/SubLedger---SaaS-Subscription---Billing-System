from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Customer:
        customer = Customer(**data, status="active")
        self.db.add(customer)
        self.db.flush()
        return customer

    def get(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.scalar(select(Customer).where(Customer.email == email))

    def list_all(self) -> list[Customer]:
        return list(self.db.scalars(select(Customer).order_by(Customer.id)).all())
