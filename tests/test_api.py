import threading
from app import app as flask_app

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


def test_concurrent_votes_from_different_voters_all_count(client):
    create_response = client.post("/api/polls", json={
        "question": "Concurrency test",
        "options": ["A", "B"]
    })
    poll_data = create_response.get_json()
    poll_id = poll_data["id"]
    option_id = poll_data["options"][0]["id"]

    NUM_VOTERS = 20
    results = []

    def vote_as_new_voter():
        # each thread gets its own test client = its own separate
        # voter identity/cookie, simulating a genuinely different person
        with flask_app.test_client() as voter_client:
            response = voter_client.post(
                f"/api/polls/{poll_id}/vote",
                json={"option_id": option_id}
            )
            results.append(response.status_code)

    threads = [threading.Thread(target=vote_as_new_voter) for _ in range(NUM_VOTERS)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # every single vote should have succeeded
    assert results.count(200) == NUM_VOTERS

    final = client.get(f"/api/polls/{poll_id}").get_json()
    final_count = final["options"][0]["vote_count"]
    assert final_count == NUM_VOTERS