import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app



client = TestClient(app)


def create_sample_todo(
    title: str = "Test todo",
    description: str = "Test description",
    completed: bool = False,
):
    payload = {
        "title": title,
        "description": description,
        "completed": completed,
    }
    response = client.post("/todos/", json=payload)
    assert response.status_code in (200, 201)
    return response.json()


def test_create_todo_and_get_by_id():
    # Arrange
    created = create_sample_todo(title="Buy milk", description="2L milk")
    todo_id = created.get("id")

    # Act
    get_response = client.get(f"/todos/{todo_id}")

    # Assert
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Buy milk"
    assert "description" in data


def test_read_all_todos_contains_created_item():
    # Arrange
    created = create_sample_todo(title="Task in list", description="Check presence")
    todo_id = created.get("id")

    # Act
    response = client.get("/todos/")

    # Assert
    assert response.status_code == 200
    todos = response.json()
    ids = [item.get("id") for item in todos]
    assert todo_id in ids


def test_update_todo_changes_fields():
    # Arrange
    created = create_sample_todo(title="Old title", description="Old desc")
    todo_id = created.get("id")

    updated_payload = {
        "title": "New title",
        "description": "New description",
        "completed": True,
    }

    # Act
    update_response = client.put(f"/todos/{todo_id}", json=updated_payload)

    # Assert
    assert update_response.status_code in (200, 202)
    updated = update_response.json()
    assert updated["id"] == todo_id
    assert updated["title"] == "New title"
    assert updated["description"] == "New description"

    if "completed" in updated:
        assert updated["completed"] is True


def test_delete_todo_removes_it():
    # Arrange
    created = create_sample_todo(title="To be deleted", description="Tmp")
    todo_id = created.get("id")

    # Act
    delete_response = client.delete(f"/todos/{todo_id}")

    # Assert
    assert delete_response.status_code in (200, 204)

    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404


def test_create_todo_without_title_returns_validation_error():
    # Arrange
    payload = {
        "description": "No title here",
        "completed": False,
    }

    # Act
    response = client.post("/todos/", json=payload)

    # Assert
    assert response.status_code == 422
