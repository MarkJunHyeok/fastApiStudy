from database.orm import ToDo


def test_health_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_get_todos(client, mocker):
    mocker.patch("main.get_todos", return_value=[
        ToDo(id=1, contents="FastAPI Section 0", is_done=False),
        ToDo(id=2, contents="FastAPI Section 1", is_done=False)
    ])

    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 1, "contents": "FastAPI Section 0", "is_done": False},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False}
        ]
    }


def test_get_todo(client, mocker):
    mocker.patch(
        "main.get_todo_by_id",
        return_value=ToDo(id=1, contents="FastAPI Section 0", is_done=False)
    )

    response = client.get("/todos/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "FastAPI Section 0", "is_done": False}


def test_get_todo_fail(client, mocker):
    mocker.patch(
        "main.get_todo_by_id",
        return_value=None
    )

    response = client.get("/todos/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo Not Found"}


def test_create_todo(client, mocker):
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch(
        "main.create_todo",
        return_value=ToDo(id=1, contents="FastAPI Section 0", is_done=False)
    )

    body = {
        "contents": "Test",
        "is_done": False
    }
    response = client.post("/todos", json=body)

    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == 'Test'
    assert create_spy.spy_return.is_done is False
    assert response.status_code == 201
    assert response.json() == {"id": 1, "contents": "FastAPI Section 0", "is_done": False}


def test_update_todo(client, mocker):
    mocker.patch(
        "main.get_todo_by_id",
        return_value=ToDo(id=1, contents="FastAPI Section 0", is_done=True)
    )

    undone = mocker.patch.object(ToDo, "undone")

    mocker.patch(
        "main.update_todo",
        return_value=ToDo(id=1, contents="FastAPI Section 0", is_done=False)
    )

    response = client.patch("/todos/1", json={"is_done": False})

    undone.assert_called_once_with()

    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "FastAPI Section 0", "is_done": False}


def test_delete_todo(client, mocker):
    mocker.patch(
        "main.get_todo_by_id",
        return_value=ToDo(id=1, contents="FastAPI Section 0", is_done=True)
    )

    response = client.delete("/todos/1")

    assert response.status_code == 204


def test_delete_todo_fail(client, mocker):
    mocker.patch(
        "main.get_todo_by_id",
        return_value=None
    )

    response = client.delete("/todos/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo Not Found"}
