from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subscription


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Subscription:
        subscription = Subscription(**data)
        self.db.add(subscription)
        self.db.flush()
        return subscription

    def get(self, subscription_id: int) -> Subscription | None:
        return self.db.get(Subscription, subscription_id)

    def list_all(self) -> list[Subscription]:
        return list(self.db.scalars(select(Subscription).order_by(Subscription.id)).all())

    def has_active_for_customer_plan(self, customer_id: int, plan_id: int) -> bool:
        subscription_id = self.db.scalar(
            select(Subscription.id).where(
                Subscription.customer_id == customer_id,
                Subscription.plan_id == plan_id,
                Subscription.status == "active",
            ).limit(1)
        )
        return subscription_id is not None
