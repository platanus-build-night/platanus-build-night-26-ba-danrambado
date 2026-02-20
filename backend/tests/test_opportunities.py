def test_list_opportunities_empty(client):
    response = client.get("/api/opportunities")
    assert response.status_code == 200
    assert response.json() == []


def test_create_opportunity_returns_201(client):
    # Create a user to use as poster
    user_resp = client.post(
        "/api/users",
        json={
            "name": "Poster",
            "bio": "Poster bio",
            "skills": [],
            "interests": [],
            "open_to": [],
        },
    )
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]

    response = client.post(
        "/api/opportunities",
        json={
            "title": "Test Job",
            "description": "A test opportunity",
            "type": "job",
            "posted_by": user_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["opportunity"]["title"] == "Test Job"
    assert data["opportunity"]["posted_by"] == user_id
    assert data["matches"] == []


def test_get_opportunity_returns_200(client):
    user_resp = client.post(
        "/api/users",
        json={
            "name": "Poster",
            "bio": "",
            "skills": [],
            "interests": [],
            "open_to": [],
        },
    )
    user_id = user_resp.json()["id"]
    create = client.post(
        "/api/opportunities",
        json={
            "title": "Get Me",
            "description": "Desc",
            "type": "project",
            "posted_by": user_id,
        },
    )
    assert create.status_code == 201
    opp_id = create.json()["opportunity"]["id"]

    response = client.get(f"/api/opportunities/{opp_id}")
    assert response.status_code == 200
    assert response.json()["opportunity"]["title"] == "Get Me"


def test_get_opportunity_not_found_returns_404(client):
    response = client.get("/api/opportunities/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Opportunity not found"


def test_create_opportunity_invalid_type_returns_400(client):
    user_resp = client.post(
        "/api/users",
        json={
            "name": "Poster",
            "bio": "",
            "skills": [],
            "interests": [],
            "open_to": [],
        },
    )
    user_id = user_resp.json()["id"]

    response = client.post(
        "/api/opportunities",
        json={
            "title": "Bad",
            "description": "Desc",
            "type": "invalid_type",
            "posted_by": user_id,
        },
    )
    assert response.status_code == 400
    assert "Invalid type" in response.json()["detail"]


def test_create_opportunity_user_not_found_returns_400(client):
    response = client.post(
        "/api/opportunities",
        json={
            "title": "Bad",
            "description": "Desc",
            "type": "job",
            "posted_by": "nonexistent-user-id",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User not found"
