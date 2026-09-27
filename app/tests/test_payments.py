from datetime import datetime, timedelta


def create_booking(client, headers):
    centre_response = client.post(
        "/centres",
        headers=headers,
        json={
            "name": "Payment Test Centre",
            "location": "Jamshedpur",
        },
    )

    assert centre_response.status_code == 200
    centre_id = centre_response.json()["id"]

    test_response = client.post(
        "/tests",
        headers=headers,
        json={
            "name": "Payment Test",
            "price": 500,
        },
    )

    assert test_response.status_code == 200
    test_id = test_response.json()["id"]

    mapping_response = client.post(
        f"/centres/{centre_id}/tests/{test_id}",
        headers=headers,
    )

    assert mapping_response.status_code == 200

    booking_response = client.post(
        "/bookings",
        headers=headers,
        json={
            "test_id": test_id,
            "centre_id": centre_id,
            "appointment_datetime": (
                datetime.now() + timedelta(days=1)
            ).isoformat(),
        },
    )

    assert booking_response.status_code == 200

    return booking_response.json()


def test_successful_payment(client, auth_headers):
    booking = create_booking(client, auth_headers)

    assert booking["status"] == "PENDING"

    response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["booking_id"] == booking["id"]
    assert data["amount"] == 500
    assert data["status"] == "SUCCESS"

    booking_response = client.get(
        f"/bookings/{booking['id']}",
        headers=auth_headers,
    )

    assert booking_response.status_code == 200
    assert booking_response.json()["status"] == "CONFIRMED"

def test_failed_payment(client, auth_headers):
    booking = create_booking(client, auth_headers)

    assert booking["status"] == "PENDING"

    response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "status": "FAILED",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["booking_id"] == booking["id"]
    assert data["amount"] == 500
    assert data["status"] == "FAILED"

    booking_response = client.get(
        f"/bookings/{booking['id']}",
        headers=auth_headers,
    )

    assert booking_response.status_code == 200
    assert booking_response.json()["status"] == "FAILED"

def test_duplicate_payment(client, auth_headers):
    booking = create_booking(client, auth_headers)

    first_response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Payment can only be made for a pending booking"
    )

def test_payment_webhook(client, auth_headers):
    booking = create_booking(client, auth_headers)

    response = client.post(
        "/payments/webhook/",
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
            "provider_event_id": "evt_test_001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Webhook processed successfully"
    assert "payment_id" in data

    booking_response = client.get(
        f"/bookings/{booking['id']}",
        headers=auth_headers,
    )

    assert booking_response.status_code == 200
    assert booking_response.json()["status"] == "CONFIRMED"

def test_payment_webhook_idempotency(client, auth_headers):
    booking = create_booking(client, auth_headers)

    payload = {
        "booking_id": booking["id"],
        "status": "SUCCESS",
        "provider_event_id": "evt_idempotency_001",
    }

    first_response = client.post(
        "/payments/webhook/",
        json=payload,
    )

    assert first_response.status_code == 200

    first_data = first_response.json()

    assert first_data["message"] == "Webhook processed successfully"

    second_response = client.post(
        "/payments/webhook/",
        json=payload,
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    assert second_data["message"] == "Webhook already processed"
    assert second_data["payment_id"] == first_data["payment_id"]

def test_payment_webhook_invalid_booking(client):
    response = client.post(
        "/payments/webhook/",
        json={
            "booking_id": 99999,
            "status": "SUCCESS",
            "provider_event_id": "evt_invalid_booking",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"

def test_payment_webhook_invalid_status(client, auth_headers):
    booking = create_booking(client, auth_headers)

    response = client.post(
        "/payments/webhook/",
        json={
            "booking_id": booking["id"],
            "status": "REFUNDED",
            "provider_event_id": "evt_invalid_status",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid payment status"

def test_webhook_cannot_process_non_pending_booking(client, auth_headers):
    booking = create_booking(client, auth_headers)

    # First webhook succeeds and confirms the booking
    first_webhook = client.post(
        "/payments/webhook/",
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
            "provider_event_id": "evt_completed_001",
        },
    )

    assert first_webhook.status_code == 200

    # A different webhook attempts to change the confirmed booking
    second_webhook = client.post(
        "/payments/webhook/",
        json={
            "booking_id": booking["id"],
            "status": "FAILED",
            "provider_event_id": "evt_completed_002",
        },
    )

    assert second_webhook.status_code == 400
    assert (
        second_webhook.json()["detail"]
        == "Payment can only be processed for a pending booking"
    )