import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_state = copy.deepcopy(activities)
    test_client = TestClient(app)

    yield test_client

    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_duplicate_registration_is_rejected(client):
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate-test@example.com"

    # Act
    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    second_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up"
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_participant_removes_email(client):
    # Arrange
    activity_name = "Programming Class"
    email = "unregister-test@example.com"

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    delete_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_activity_full_rejects_new_signup(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@example.com"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student-{index}@example.com" for index in range(activity["max_participants"])
    ]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
