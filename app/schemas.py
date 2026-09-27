from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CentreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    location: str = Field(min_length=2, max_length=500)


class CentreResponse(BaseModel):
    id: int
    name: str
    location: str


class TestCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    price: float = Field(gt=0)


class TestResponse(BaseModel):
    id: int
    name: str
    price: float

class BookingCreate(BaseModel):
    test_id: int
    centre_id: int
    appointment_datetime: datetime


class BookingResponse(BaseModel):
    id: int
    user_id: int
    test_id: int
    centre_id: int
    appointment_datetime: datetime
    amount: float
    status: str


class PaymentCreate(BaseModel):
    booking_id: int
    status: str


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: float
    status: str


class PaymentWebhookRequest(BaseModel):
    booking_id: int
    status: str
    provider_event_id: str