from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.utils import get_current_user
from app.database import get_db
from app.models import Test, User
from app.schemas import TestCreate, TestResponse


router = APIRouter(
    prefix="/tests",
    tags=["Tests"],
)


@router.post(
    "",
    response_model=TestResponse,
)
def create_test(
    data: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = Test(
        name=data.name,
        price=data.price,
    )

    db.add(test)
    db.commit()
    db.refresh(test)

    return test


@router.get(
    "",
    response_model=list[TestResponse],
)
def get_tests(
    db: Session = Depends(get_db),
):
    tests = (
        db.query(Test)
        .order_by(Test.id)
        .all()
    )

    return tests