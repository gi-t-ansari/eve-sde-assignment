from datetime import datetime, timedelta

def test_create_booking(client,auth_headers):
    headers = auth_headers

    centre_response = client.post(
        "/centres",
        headers=headers,
        json={
            "name": "Test Diagnostic Centre",
            "location": "Jamshedpur",
        },
    )

    assert centre_response.status_code == 200
    centre_id = centre_response.json()["id"]

    test_response = client.post(
        "/tests",
        headers=headers,
        json={
            "name": "Blood Test",
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

    appointment_time = (
        datetime.now() + timedelta(days=1)
    ).isoformat()

    booking_response = client.post(
        "/bookings",
        headers=headers,
        json={
            "test_id": test_id,
            "centre_id": centre_id,
            "appointment_datetime": appointment_time,
        },
    )

    assert booking_response.status_code == 200

    data = booking_response.json()

    assert data["test_id"] == test_id
    assert data["centre_id"] == centre_id
    assert data["amount"] == 500
    assert data["status"] == "PENDING"

def test_create_booking_when_test_not_available(client, auth_headers):
    centre_response = client.post(
        "/centres",
        headers=auth_headers,
        json={
            "name": "Another Diagnostic Centre",
            "location": "Jamshedpur",
        },
    )

    assert centre_response.status_code == 200
    centre_id = centre_response.json()["id"]

    test_response = client.post(
        "/tests",
        headers=auth_headers,
        json={
            "name": "MRI Scan",
            "price": 1500,
        },
    )

    assert test_response.status_code == 200
    test_id = test_response.json()["id"]

    # Intentionally NOT linking the test to the centre.

    appointment_time = (
        datetime.now() + timedelta(days=1)
    ).isoformat()

    response = client.post(
        "/bookings",
        headers=auth_headers,
        json={
            "test_id": test_id,
            "centre_id": centre_id,
            "appointment_datetime": appointment_time,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "This test is not available at the selected centre"
    )

def test_duplicate_centre_test_mapping(client, auth_headers):
    centre_response = client.post(
        "/centres",
        headers=auth_headers,
        json={
            "name": "Test Centre",
            "location": "Jamshedpur",
        },
    )

    assert centre_response.status_code == 200
    centre_id = centre_response.json()["id"]

    test_response = client.post(
        "/tests",
        headers=auth_headers,
        json={
            "name": "Blood Test",
            "price": 500,
        },
    )

    assert test_response.status_code == 200
    test_id = test_response.json()["id"]

    first_mapping = client.post(
        f"/centres/{centre_id}/tests/{test_id}",
        headers=auth_headers,
    )

    assert first_mapping.status_code == 200

    second_mapping = client.post(
        f"/centres/{centre_id}/tests/{test_id}",
        headers=auth_headers,
    )

    assert second_mapping.status_code == 400
    assert second_mapping.json()["detail"] == "Test already available at this centre"