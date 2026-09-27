# EVE Healthcare Backend

Backend service for diagnostic test bookings and simulated payments, built as part of the EVE Healthcare SDE Intern Backend Engineering Assignment.

## Tech Stack

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT Authentication
- Argon2 Password Hashing
- Pytest

## Features

- User signup and login
- JWT-based authentication
- Diagnostic centre management
- Diagnostic test management
- Centre-test availability mapping
- Diagnostic test bookings
- Booking ownership protection
- Simulated payments
- Payment success/failure handling
- Payment webhook processing
- Webhook idempotency
- Booking/payment state validation
- Automated API tests
- Swagger/OpenAPI documentation

---

## Project Structure

```text
eve-healthcare-backend/
│
├── app/
│   ├── auth/
│   │   ├── routes.py
│   │   └── utils.py
│   │
│   ├── bookings/
│   │   └── routes.py
│   │
│   ├── centres/
│   │   └── routes.py
│   │
│   ├── payments/
│   │   └── routes.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_bookings.py
│   │   └── test_payments.py
│   │
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md