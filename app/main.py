from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database import Base, engine
from app.models import User, DiagnosticCentre, Test, CentreTest

from app.auth.routes import router as auth_router
from app.centres.routes import router as centre_router
from app.tests.routes import router as test_router
from app.bookings.routes import router as booking_router
from app.payments.routes import router as payment_router




# Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="EVE Healthcare API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(centre_router)
app.include_router(test_router)
app.include_router(booking_router)
app.include_router(payment_router)


@app.get("/")
def root():
    return {"message": "EVE Healthcare API is running"}


@app.get("/health/db")
def database_health():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "result": result.scalar(),
        }