from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.payment import (
    PaymentResponse,
    PaymentStatusTransitionRequest,
)
from app.services.payment_service import (
    create_payment,
    get_application_payments,
    transition_payment_status,
)

router = APIRouter(tags=["Payments"])


@router.post(
    "/applications/{application_id}/payments",
    response_model=PaymentResponse,
)
@router.post(
    "/applications/{application_id}/payments/",
    response_model=PaymentResponse,
    include_in_schema=False,
)
def create_payment_api(
    application_id: str,
    db: Session = Depends(get_db),
):
    result = create_payment(db, application_id)

    if result == "APPLICATION_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    if result == "APPLICATION_NOT_SANCTIONED":
        raise HTTPException(
            status_code=409,
            detail="Application is not sanctioned",
        )

    if result == "PAYMENT_ALREADY_EXISTS":
        raise HTTPException(
            status_code=409,
            detail="Payment already exists",
        )

    return result


@router.get(
    "/applications/{application_id}/payments",
    response_model=list[PaymentResponse],
)
@router.get(
    "/applications/{application_id}/payments/",
    response_model=list[PaymentResponse],
    include_in_schema=False,
)
def list_application_payments_api(
    application_id: str,
    db: Session = Depends(get_db),
):
    result = get_application_payments(db, application_id)

    if result == "APPLICATION_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return result


@router.post(
    "/payments/{payment_id}/status",
    response_model=PaymentResponse,
)
@router.post(
    "/payments/{payment_id}/status/",
    response_model=PaymentResponse,
    include_in_schema=False,
)
def transition_payment_status_api(
    payment_id: str,
    payload: PaymentStatusTransitionRequest,
    db: Session = Depends(get_db),
):
    result = transition_payment_status(db, payment_id, payload.status)

    if result == "PAYMENT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    if result == "INVALID_STATUS":
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status",
        )

    if result == "INVALID_TRANSITION":
        raise HTTPException(
            status_code=409,
            detail="Invalid payment status transition",
        )

    return result
