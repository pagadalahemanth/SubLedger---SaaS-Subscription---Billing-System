from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleError, NotFoundError
from app.repositories.plan_repository import PlanRepository
from app.schemas import PlanCreate, PlanPatch
from app.services.common import commit_changes


class PlanService:
    def __init__(self, db: Session, repository: PlanRepository):
        self.db = db
        self.repository = repository

    def create_plan(self, payload: PlanCreate):
        if payload.price <= 0:
            raise BusinessRuleError("Plan price must be greater than 0.")
        plan = self.repository.create(payload.model_dump())
        commit_changes(self.db)
        self.db.refresh(plan)
        return plan

    def list_plans(self):
        return self.repository.list_all()

    def update_plan(self, plan_id: int, payload: PlanPatch):
        plan = self.repository.get(plan_id)
        if plan is None:
            raise NotFoundError("Plan not found.")

        changes = payload.model_dump(exclude_unset=True)
        for field in ("name", "billing_cycle", "price", "currency", "status"):
            if field in changes and changes[field] is None:
                raise BusinessRuleError(f"{field} cannot be null.")
        if "price" in changes and changes["price"] <= 0:
            raise BusinessRuleError("Plan price must be greater than 0.")
        if not changes:
            return plan

        self.repository.update(plan, changes)
        commit_changes(self.db)
        self.db.refresh(plan)
        return plan
