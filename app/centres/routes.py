from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.utils import get_current_user
from app.database import get_db
from app.models import (
    CentreTest,
    DiagnosticCentre,
    Test,
    User,
)
from app.schemas import (
    CentreCreate,
    CentreResponse,
    TestResponse,
)


router = APIRouter(
    prefix="/centres",
    tags=["Diagnostic Centres"],
)


@router.post(
    "",
    response_model=CentreResponse,
)
def create_centre(
    data: CentreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    centre = DiagnosticCentre(
        name=data.name,
        location=data.location,
    )

    db.add(centre)
    db.commit()
    db.refresh(centre)

    return centre


@router.get(
    "",
    response_model=list[CentreResponse],
)
def get_centres(
    db: Session = Depends(get_db),
):
    centres = (
        db.query(DiagnosticCentre)
        .order_by(DiagnosticCentre.id)
        .all()
    )

    return centres


@router.post(
    "/{centre_id}/tests/{test_id}",
)
def add_test_to_centre(
    centre_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    centre = (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.id == centre_id)
        .first()
    )

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic centre not found",
        )

    test = (
        db.query(Test)
        .filter(Test.id == test_id)
        .first()
    )

    if not test:
        raise HTTPException(
            status_code=404,
            detail="Test not found",
        )

    existing_relation = (
        db.query(CentreTest)
        .filter(
            CentreTest.centre_id == centre_id,
            CentreTest.test_id == test_id,
        )
        .first()
    )

    if existing_relation:
        raise HTTPException(
            status_code=400,
            detail="Test already available at this centre",
        )

    centre_test = CentreTest(
        centre_id=centre_id,
        test_id=test_id,
    )

    db.add(centre_test)
    db.commit()

    return {
        "message": "Test added to diagnostic centre",
    }


@router.get(
    "/{centre_id}/tests",
    response_model=list[TestResponse],
)
def get_centre_tests(
    centre_id: int,
    db: Session = Depends(get_db),
):
    centre = (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.id == centre_id)
        .first()
    )

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic centre not found",
        )

    tests = (
        db.query(Test)
        .join(
            CentreTest,
            CentreTest.test_id == Test.id,
        )
        .filter(
            CentreTest.centre_id == centre_id,
        )
        .all()
    )

    return tests