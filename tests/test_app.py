from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_duplicate_registration_is_rejected():
    activity_name = "Chess Club"
    email = "duplicate-test@example.com"

    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up"

    client.delete(f"/activities/{activity_name}/unregister?email={email}")


def test_unregister_participant_removes_email():
    activity_name = "Programming Class"
    email = "unregister-test@example.com"

    client.post(f"/activities/{activity_name}/signup?email={email}")
    delete_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]
