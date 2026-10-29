from decimal import Decimal

from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleError, NotFoundError
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.payment_attempt_repository import PaymentAttemptRepository
from app.schemas import PaymentRecordRequest
from app.services.common import commit_changes
from app.services.ledger_service import LedgerService


class PaymentService:
    def __init__(
        self,
        db: Session,
        invoices: InvoiceRepository,
        payment_attempts: PaymentAttemptRepository,
        ledger_service: LedgerService,
    ):
        self.db = db
        self.invoices = invoices
        self.payment_attempts = payment_attempts
        self.ledger_service = ledger_service

    def record_payment(self, payload: PaymentRecordRequest):
        invoice = self.invoices.get(payload.invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found.")
        if payload.amount <= 0:
            raise BusinessRuleError("Payment amount must be greater than 0.")
        if payload.currency != invoice.currency:
            raise BusinessRuleError("Payment currency must match the invoice currency.")
        if invoice.status in ("paid", "void"):
            raise BusinessRuleError("Payments cannot be recorded against a paid or void invoice.")

        remaining = invoice.amount_due - invoice.amount_paid
        if payload.status == "success" and payload.amount > remaining:
            raise BusinessRuleError("Successful payment cannot exceed the remaining unpaid amount.")

        attempt = self.payment_attempts.create(
            {
                "invoice_id": invoice.id,
                "amount": payload.amount,
                "currency": payload.currency,
                "status": payload.status,
                "provider_reference": payload.provider_reference.strip(),
                "failure_reason": payload.failure_reason,
            }
        )

        if payload.status == "success":
            invoice.amount_paid += payload.amount
            invoice.status = "paid" if invoice.amount_paid == invoice.amount_due else "partially_paid"
            entry_type = "payment_success"
            description = f"Successful payment attempt {attempt.id} recorded for invoice {invoice.id}."
        else:
            # Failed attempts are recorded, but never change amount_paid or invoice status.
            entry_type = "payment_failure"
            description = f"Failed payment attempt {attempt.id} recorded for invoice {invoice.id}."

        self.ledger_service.create_entry(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            entry_type=entry_type,
            amount=payload.amount,
            currency=invoice.currency,
            reference_id=f"payment_attempt:{attempt.id}",
            description=description,
        )
        commit_changes(self.db)
        self.db.refresh(attempt)
        self.db.refresh(invoice)
        return attempt, invoice
