def test_register(client):
    response = client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@test.com"
  

def test_register_duplicate_email(client):
    client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "password123"
    })
    response = client.post("/users/register", json={
        "username": "testuser2",
        "email": "test@test.com",
        "password": "password123"
    })
    assert response.status_code == 400


def test_login(client):
    client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "password123"
    })
    response = client.post("/users/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "password123"
    })
    response = client.post("/users/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
