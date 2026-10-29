import calendar
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.repositories.customer_repository import CustomerRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas import SubscriptionCreate
from app.services.common import commit_changes


class SubscriptionService:
    def __init__(
        self,
        db: Session,
        customers: CustomerRepository,
        plans: PlanRepository,
        subscriptions: SubscriptionRepository,
    ):
        self.db = db
        self.customers = customers
        self.plans = plans
        self.subscriptions = subscriptions

    def create_subscription(self, payload: SubscriptionCreate):
        customer = self.customers.get(payload.customer_id)
        if customer is None:
            raise NotFoundError("Customer not found.")

        plan = self.plans.get(payload.plan_id)
        if plan is None:
            raise NotFoundError("Plan not found.")
        if plan.status != "active":
            raise BusinessRuleError("A subscription cannot use an inactive plan.")
        if self.subscriptions.has_active_for_customer_plan(customer.id, plan.id):
            raise ConflictError("Customer already has an active subscription to this plan.")

        start_date = payload.start_date or date.today()
        months = {"monthly": 1, "quarterly": 3, "yearly": 12}[plan.billing_cycle]
        end_date = add_months(start_date, months)
        subscription = self.subscriptions.create(
            {
                "customer_id": customer.id,
                "plan_id": plan.id,
                "status": "active",
                "start_date": start_date,
                "current_period_start": start_date,
                "current_period_end": end_date,
            }
        )
        commit_changes(self.db)
        self.db.refresh(subscription)
        return subscription

    def list_subscriptions(self):
        return self.subscriptions.list_all()

    def cancel_subscription(self, subscription_id: int):
        subscription = self.subscriptions.get(subscription_id)
        if subscription is None:
            raise NotFoundError("Subscription not found.")
        if subscription.status != "active":
            raise BusinessRuleError("Only active subscriptions can be cancelled.")

        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.now(timezone.utc)
        commit_changes(self.db)
        self.db.refresh(subscription)
        return subscription


def add_months(value: date, months: int) -> date:
    """Add calendar months while preserving the day where possible."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
