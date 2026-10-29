from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_ledger_service
from app.schemas import LedgerEntryOut
from app.services.ledger_service import LedgerService

router = APIRouter(tags=["Ledger"])


@router.get("/customers/{customer_id}/ledger", response_model=list[LedgerEntryOut])
def get_customer_ledger(
    customer_id: int,
    service: Annotated[LedgerService, Depends(get_ledger_service)],
):
    return service.get_customer_ledger(customer_id)
