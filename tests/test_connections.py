def test_send_connection(auth_client, auth_client2):
    response = auth_client.post("/connections/testuser2/send")
    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_send_connection_duplicate(auth_client, auth_client2):
    auth_client.post("/connections/testuser2/send")
    response = auth_client.post("/connections/testuser2/send")
    assert response.status_code == 400


def test_accept_connection(auth_client, auth_client2):
    auth_client.post("/connections/testuser2/send")
    response = auth_client2.put("/connections/testuser/accept")
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_decline_connection(auth_client, auth_client2):
    auth_client.post("/connections/testuser2/send")
    response = auth_client2.put("/connections/testuser/decline")
    assert response.status_code == 200
    assert response.json()["status"] == "declined"


def test_get_connections(auth_client, auth_client2):
    auth_client.post("/connections/testuser2/send")
    response = auth_client.get("/connections/?status=pending")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_connection(auth_client, auth_client2):
    auth_client.post("/connections/testuser2/send")
    response = auth_client.delete("/connections/testuser2")
    assert response.status_code == 204