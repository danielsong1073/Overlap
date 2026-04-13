from unittest.mock import patch

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


def test_get_me(auth_client):
    response = auth_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_shelf(auth_client):
    response = auth_client.get("/users/testuser/shelf")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_shelf_not_found(client):
    response = client.get("/users/nonexistent/shelf")
    assert response.status_code == 404


def test_get_suggested(auth_client, auth_client2):
    mock_metadata = {
        "title": "Dune",
        "external_id": "OL21177W",
        "cover_image": None,
        "release_year": 1965
    }
    with patch("app.services.get_book_metadata", return_value=mock_metadata):
        auth_client.post("/entries/", json={
            "media_type": "book",
            "title": "Dune",
            "status": "reading"
        })
        auth_client2.post("/entries/", json={
            "media_type": "book",
            "title": "Dune",
            "status": "reading"
        })

    response = auth_client.get("/users/suggested")
    assert response.status_code == 200
    assert response.json()[0]["username"] == "testuser2"
    assert response.json()[0]["overlap_count"] == 1


def test_get_upload_url(auth_client):
    with patch("app.routers.users.boto3.client") as mock_boto:
        mock_boto.return_value.generate_presigned_url.return_value = "https://fake-s3-url.com/upload"
        response = auth_client.get("/users/upload-url")
    assert response.status_code == 200
    assert "upload_url" in response.json()
    assert "file_key" in response.json()


def test_update_profile_picture(auth_client):
    response = auth_client.put("/users/me/profile-picture", json={
        "profile_picture_url": "https://fake-s3-url.com/image.jpg"
    })
    assert response.status_code == 200
    assert response.json()["profile_picture"] == "https://fake-s3-url.com/image.jpg"