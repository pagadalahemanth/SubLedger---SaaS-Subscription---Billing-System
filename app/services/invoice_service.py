from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleError, NotFoundError
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas import InvoiceGenerateRequest
from app.services.common import commit_changes
from app.services.ledger_service import LedgerService


class InvoiceService:
    def __init__(
        self,
        db: Session,
        subscriptions: SubscriptionRepository,
        plans: PlanRepository,
        invoices: InvoiceRepository,
        ledger_service: LedgerService,
    ):
        self.db = db
        self.subscriptions = subscriptions
        self.plans = plans
        self.invoices = invoices
        self.ledger_service = ledger_service

    def generate_invoice(self, payload: InvoiceGenerateRequest):
        subscription = self.subscriptions.get(payload.subscription_id)
        if subscription is None:
            raise NotFoundError("Subscription not found.")
        if subscription.status != "active":
            raise BusinessRuleError("Invoices can only be generated for active subscriptions.")

        plan = self.plans.get(subscription.plan_id)
        if plan is None:
            raise NotFoundError("Plan not found for this subscription.")

        if (payload.period_start is None) != (payload.period_end is None):
            raise BusinessRuleError("Provide both period_start and period_end, or neither.")
        period_start = payload.period_start or subscription.current_period_start
        period_end = payload.period_end or subscription.current_period_end
        if period_end <= period_start:
            raise BusinessRuleError("period_end must be later than period_start.")

        today = date.today()
        invoice = self.invoices.create(
            {
                "subscription_id": subscription.id,
                "customer_id": subscription.customer_id,
                # Snapshot the plan price now. Later plan changes do not alter this invoice.
                "amount_due": plan.price,
                "amount_paid": Decimal("0.00"),
                "currency": plan.currency,
                "status": "issued",
                "period_start": period_start,
                "period_end": period_end,
                "due_date": payload.due_date or today + timedelta(days=30),
            }
        )
        self.ledger_service.create_entry(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            entry_type="invoice_created",
            amount=invoice.amount_due,
            currency=invoice.currency,
            reference_id=f"invoice:{invoice.id}",
            description=f"Invoice {invoice.id} generated for subscription {subscription.id}.",
        )
        commit_changes(self.db)
        self.db.refresh(invoice)
        return invoice

    def get_invoice(self, invoice_id: int):
        invoice = self.invoices.get(invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found.")
        return invoice
