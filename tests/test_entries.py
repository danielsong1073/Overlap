def test_create_entry(auth_client):
    response = auth_client.post("/entries/", json={
        "media_type": "book",
        "title": "Dune",
        "status": "reading"
    })
    assert response.status_code == 201
    assert response.json()["title"] is not None
    assert response.json()["media_type"] == "book"


def test_get_my_entries(auth_client):
  auth_client.post("/entries/", json={
     "media_type": "book",
      "title": "Dune",
      "status": "reading"
  })
  response = auth_client.get("/entries/me")
  assert response.status_code == 200
  assert len(response.json()) == 1


def test_update_entry(auth_client):
   create_response = auth_client.post("/entries/", json={
      "media_type": "book",
      "title": "Dune",
      "status": "reading"
   })
   entry_id = create_response.json()["id"]
   response = auth_client.put(f"/entries/{entry_id}", json={
      "media_type": "book",
      "title": "Dune",
      "status": "finished"
   })
   assert response.status_code == 200
   assert response.json()["status"] == "finished"
  

def test_delete_entry(auth_client):
   create_response = auth_client.post("/entries/", json={
      "media_type": "book",
      "title": "Dune",
      "status": "reading"
   })
   entry_id = create_response.json()["id"]
   response = auth_client.delete(f"/entries/{entry_id}")
   assert response.status_code == 204

   get_response = auth_client.get("/entries/me")
   assert len(get_response.json()) == 0
  

def test_delete_entry_not_found(auth_client):
   response = auth_client.delete("/entries/999")
   assert response.status_code == 404