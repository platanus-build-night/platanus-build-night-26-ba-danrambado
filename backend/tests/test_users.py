def test_list_users_empty(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == []


def test_create_user_returns_201(client):
    response = client.post(
        "/api/users",
        json={
            "name": "Test User",
            "bio": "A bio",
            "skills": ["Python"],
            "interests": ["AI"],
            "open_to": ["jobs"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["bio"] == "A bio"
    assert "id" in data
    assert "created_at" in data


def test_get_user_returns_200(client):
    create = client.post(
        "/api/users",
        json={
            "name": "Get Me",
            "bio": "Bio",
            "skills": [],
            "interests": [],
            "open_to": [],
        },
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Me"


def test_get_user_not_found_returns_404(client):
    response = client.get("/api/users/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_list_users_after_create(client):
    client.post(
        "/api/users",
        json={
            "name": "One",
            "bio": "",
            "skills": [],
            "interests": [],
            "open_to": [],
        },
    )
    response = client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "One"
