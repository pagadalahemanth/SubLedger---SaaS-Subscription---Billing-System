from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_customer_service
from app.schemas import CustomerCreate, CustomerOut
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return service.create_customer(payload)


@router.get("", response_model=list[CustomerOut])
def list_customers(service: Annotated[CustomerService, Depends(get_customer_service)]):
    return service.list_customers()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return service.get_customer(customer_id)
