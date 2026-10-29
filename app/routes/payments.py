from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_payment_service
from app.schemas import PaymentRecordRequest, PaymentRecordResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/record", response_model=PaymentRecordResponse, status_code=status.HTTP_201_CREATED)
def record_payment(
    payload: PaymentRecordRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
):
    attempt, invoice = service.record_payment(payload)
    return {"payment_attempt": attempt, "invoice": invoice}
