from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.utils import get_current_user
from app.database import get_db
from app.models import (
    Booking,
    BookingStatus,
    CentreTest,
    DiagnosticCentre,
    Test,
    User,
)
from app.schemas import BookingCreate, BookingResponse


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Check that the centre exists
    centre = (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.id == data.centre_id)
        .first()
    )

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic centre not found",
        )

    # 2. Check that the test exists
    test = (
        db.query(Test)
        .filter(Test.id == data.test_id)
        .first()
    )

    if not test:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic test not found",
        )

    # 3. Check that this centre offers this test
    centre_test = (
        db.query(CentreTest)
        .filter(
            CentreTest.centre_id == data.centre_id,
            CentreTest.test_id == data.test_id,
        )
        .first()
    )

    if not centre_test:
        raise HTTPException(
            status_code=400,
            detail="This test is not available at the selected centre",
        )

    # 4. Create booking
    booking = Booking(
        user_id=current_user.id,
        test_id=test.id,
        centre_id=centre.id,
        appointment_datetime=data.appointment_datetime,
        amount=test.price,
        status=BookingStatus.PENDING,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


@router.get(
    "",
    response_model=list[BookingResponse],
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return bookings


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    return booking