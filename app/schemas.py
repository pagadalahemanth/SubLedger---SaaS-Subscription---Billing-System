"""Pydantic request and response schemas for the HTTP API."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

BillingCycle = Literal["monthly", "quarterly", "yearly"]
RecordStatus = Literal["active", "inactive"]
PaymentStatus = Literal["success", "failed"]


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid", str_strip_whitespace=True)


def normalize_currency(value: str) -> str:
    return value.strip().upper()


class PlanCreate(APIModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    billing_cycle: BillingCycle
    price: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return normalize_currency(value)


class PlanPatch(APIModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    billing_cycle: BillingCycle | None = None
    price: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    status: RecordStatus | None = None

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str | None) -> str | None:
        return normalize_currency(value) if value is not None else None


class PlanOut(APIModel):
    id: int
    name: str
    description: str | None
    billing_cycle: str
    price: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime


class CustomerCreate(APIModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    company_name: str | None = Field(default=None, max_length=200)


class CustomerOut(APIModel):
    id: int
    name: str
    email: EmailStr
    company_name: str | None
    status: str
    created_at: datetime


class SubscriptionCreate(APIModel):
    customer_id: int = Field(gt=0)
    plan_id: int = Field(gt=0)
    start_date: date | None = None


class SubscriptionOut(APIModel):
    id: int
    customer_id: int
    plan_id: int
    status: str
    start_date: date
    current_period_start: date
    current_period_end: date
    cancelled_at: datetime | None
    created_at: datetime


class CancelSubscriptionOut(APIModel):
    id: int
    status: str
    cancelled_at: datetime | None


class InvoiceGenerateRequest(APIModel):
    subscription_id: int = Field(gt=0)
    period_start: date | None = None
    period_end: date | None = None
    due_date: date | None = None


class InvoiceOut(APIModel):
    id: int
    subscription_id: int
    customer_id: int
    amount_due: Decimal
    amount_paid: Decimal
    currency: str
    status: str
    period_start: date
    period_end: date
    due_date: date
    created_at: datetime


class PaymentRecordRequest(APIModel):
    invoice_id: int = Field(gt=0)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    status: PaymentStatus
    provider_reference: str = Field(min_length=1, max_length=150)
    failure_reason: str | None = None

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return normalize_currency(value)


class PaymentAttemptOut(APIModel):
    id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: str
    provider_reference: str
    failure_reason: str | None
    created_at: datetime


class PaymentRecordResponse(APIModel):
    payment_attempt: PaymentAttemptOut
    invoice: InvoiceOut


class LedgerEntryOut(APIModel):
    id: int
    customer_id: int
    invoice_id: int
    entry_type: str
    amount: Decimal
    currency: str
    reference_id: str
    description: str
    created_at: datetime
