"""FastAPI dependency wiring: choose repositories and services in one place."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.customer_repository import CustomerRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.ledger_repository import LedgerRepository
from app.repositories.payment_attempt_repository import PaymentAttemptRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.customer_service import CustomerService
from app.services.invoice_service import InvoiceService
from app.services.ledger_service import LedgerService
from app.services.payment_service import PaymentService
from app.services.plan_service import PlanService
from app.services.subscription_service import SubscriptionService


DBSession = Annotated[Session, Depends(get_db)]


def get_plan_service(db: DBSession) -> PlanService:
    return PlanService(db, PlanRepository(db))


def get_customer_service(db: DBSession) -> CustomerService:
    return CustomerService(db, CustomerRepository(db))


def get_subscription_service(db: DBSession) -> SubscriptionService:
    return SubscriptionService(
        db,
        CustomerRepository(db),
        PlanRepository(db),
        SubscriptionRepository(db),
    )


def get_ledger_service(db: DBSession) -> LedgerService:
    return LedgerService(db, CustomerRepository(db), LedgerRepository(db))


def get_invoice_service(db: DBSession) -> InvoiceService:
    return InvoiceService(
        db,
        SubscriptionRepository(db),
        PlanRepository(db),
        InvoiceRepository(db),
        LedgerService(db, CustomerRepository(db), LedgerRepository(db)),
    )


def get_payment_service(db: DBSession) -> PaymentService:
    return PaymentService(
        db,
        InvoiceRepository(db),
        PaymentAttemptRepository(db),
        LedgerService(db, CustomerRepository(db), LedgerRepository(db)),
    )
