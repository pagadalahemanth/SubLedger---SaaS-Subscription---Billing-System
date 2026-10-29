from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Plan


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Plan:
        plan = Plan(**data, status="active")
        self.db.add(plan)
        self.db.flush()
        return plan

    def get(self, plan_id: int) -> Plan | None:
        return self.db.get(Plan, plan_id)

    def list_all(self) -> list[Plan]:
        return list(self.db.scalars(select(Plan).order_by(Plan.id)).all())

    def update(self, plan: Plan, changes: dict) -> Plan:
        for field, value in changes.items():
            setattr(plan, field, value)
        self.db.flush()
        return plan
