def test_create_poll_returns_201(client):
    response = client.post("/api/polls", json={
        "question": "Tabs or spaces?",
        "options": ["Tabs", "Spaces"]
    })
    assert response.status_code == 201

    body = response.get_json()
    assert body["question"] == "Tabs or spaces?"
    assert len(body["options"]) == 2


def test_create_poll_without_question_returns_400(client):
    response = client.post("/api/polls", json={"options": ["A", "B"]})
    assert response.status_code == 400


def test_create_poll_with_one_option_returns_400(client):
    response = client.post("/api/polls", json={
        "question": "Test?",
        "options": ["Only one"]
    })
    assert response.status_code == 400


def test_get_all_polls_returns_created_polls(client):
    client.post("/api/polls", json={"question": "Q1", "options": ["A", "B"]})
    client.post("/api/polls", json={"question": "Q2", "options": ["C", "D"]})

    response = client.get("/api/polls")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_single_poll_by_id(client):
    create_response = client.post("/api/polls", json={"question": "Q1", "options": ["A", "B"]})
    poll_id = create_response.get_json()["id"]

    response = client.get(f"/api/polls/{poll_id}")
    assert response.status_code == 200
    assert response.get_json()["question"] == "Q1"


def test_get_nonexistent_poll_returns_404(client):
    response = client.get("/api/polls/999")
    assert response.status_code == 404


def test_cast_vote_succeeds(client):
    create_response = client.post("/api/polls", json={"question": "Q1", "options": ["A", "B"]})
    poll_data = create_response.get_json()
    poll_id = poll_data["id"]
    option_id = poll_data["options"][0]["id"]

    response = client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})
    assert response.status_code == 200
    assert response.get_json()["options"][0]["vote_count"] == 1


def test_duplicate_vote_from_same_voter_returns_409(client):
    create_response = client.post("/api/polls", json={"question": "Q1", "options": ["A", "B"]})
    poll_data = create_response.get_json()
    poll_id = poll_data["id"]
    option_id = poll_data["options"][0]["id"]

    client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})
    second_response = client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})

    assert second_response.status_code == 409


def test_vote_on_nonexistent_poll_returns_404(client):
    response = client.post("/api/polls/999/vote", json={"option_id": 1})
    assert response.status_code == 404


def test_vote_with_option_from_different_poll_returns_400(client):
    poll1 = client.post("/api/polls", json={"question": "Q1", "options": ["A", "B"]}).get_json()
    poll2 = client.post("/api/polls", json={"question": "Q2", "options": ["C", "D"]}).get_json()

    wrong_option_id = poll1["options"][0]["id"]

    response = client.post(f"/api/polls/{poll2['id']}/vote", json={"option_id": wrong_option_id})
    assert response.status_code == 400