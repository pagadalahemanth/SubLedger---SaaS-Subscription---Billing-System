from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_invoice_service
from app.schemas import InvoiceGenerateRequest, InvoiceOut
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/generate", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def generate_invoice(
    payload: InvoiceGenerateRequest,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
):
    return service.generate_invoice(payload)


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
):
    return service.get_invoice(invoice_id)
