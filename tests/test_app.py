import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: preserve global state before each test
    original = copy.deepcopy(activities)
    yield
    # Assert / Teardown: restore state so tests remain isolated
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Chess Club" in result
    assert "Programming Class" in result


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_already_signed_up():
    # Arrange
    client = TestClient(app)
    existing_email = activities["Chess Club"]["participants"][0]

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] in [
        "Student is already signed up for this activity",
        "Student already signed up for this activity",
    ]


def test_signup_for_activity_not_found():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": "x@x.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    # Arrange
    client = TestClient(app)
    existing_email = activities["Chess Club"]["participants"][0]

    # Act
    response = client.delete(f"/activities/Chess Club/participants/{existing_email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {existing_email} from Chess Club"}
    assert existing_email not in activities["Chess Club"]["participants"]


def test_remove_participant_activity_not_found():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.delete("/activities/Nonexistent/participants/student@x.com")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_not_found():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.delete("/activities/Chess Club/participants/missing@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
