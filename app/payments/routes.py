from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Booking,
    Payment,
    PaymentStatus,
    BookingStatus,
)
from app.schemas import PaymentCreate, PaymentResponse, PaymentWebhookRequest
from app.auth.utils import get_current_user

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/", response_model=PaymentResponse)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == data.booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    if data.status not in [PaymentStatus.SUCCESS, PaymentStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status",
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Payment can only be made for a pending booking",
        )

    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=data.status,
    )

    if data.status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.post("/webhook/")
def payment_webhook(
    data: PaymentWebhookRequest,
    db: Session = Depends(get_db),
):
    # Check if this provider event was already processed
    existing_payment = (
        db.query(Payment)
        .filter(Payment.provider_event_id == data.provider_event_id)
        .first()
    )

    if existing_payment:
        return {
            "message": "Webhook already processed",
            "payment_id": existing_payment.id,
        }

    # Find the booking
    booking = (
        db.query(Booking)
        .filter(Booking.id == data.booking_id)
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    # Booking must still be pending
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Payment can only be processed for a pending booking",
        )

    # Validate payment status
    if data.status not in [PaymentStatus.SUCCESS, PaymentStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status",
        )

    # Create payment record
    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=data.status,
        provider_event_id=data.provider_event_id,
    )

    # Update booking status
    if data.status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Webhook processed successfully",
        "payment_id": payment.id,
    }