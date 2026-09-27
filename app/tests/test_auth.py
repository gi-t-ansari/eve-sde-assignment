from datetime import datetime, timedelta

def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User created successfully"
    assert data["user"]["email"] == "test@example.com"
    assert "id" in data["user"]


def test_signup_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
    }

    first_response = client.post(
        "/auth/signup",
        json=payload,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/signup",
        json=payload,
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert data["detail"] == "Email already registered"

def test_login(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert signup_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    client.post(
        "/auth/signup",
        json={
            "email": "wrong-password@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong-password@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid email or password"

def test_get_current_user(client):
    client.post(
        "/auth/signup",
        json={
            "email": "me@example.com",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "me@example.com"

def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401



