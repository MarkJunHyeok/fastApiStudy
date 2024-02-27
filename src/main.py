from typing import List

from fastapi import FastAPI, Body, HTTPException, Depends
from sqlalchemy.orm import Session

from database.conection import get_db
from database.orm import ToDo
from database.repository import get_todos, get_todo_by_id, create_todo, update_todo, delete_todo
from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema

app = FastAPI()


@app.get("/")
def health_check_handler():
    return {"ping": "pong"}


todo_data = {
    1: {
        "id": 1,
        "contents": "실전! FastAPI 섹션 0 수강",
        "is_done": True,
    },
    2: {
        "id": 2,
        "contents": "실전! FastAPI 섹션 1 수강",
        "is_done": False,
    },
    3: {
        "id": 3,
        "contents": "실전! FastAPI 섹션 2 수강",
        "is_done": False,
    }
}


@app.get("/todos", status_code=200)
def get_todos_handler(
        order: str | None = None,
        session: Session = Depends(get_db)
) -> ToDoListSchema:
    todos: List[ToDo] = get_todos(session)

    if order == "DESC":
        return ToDoListSchema(
            todos=[ToDoSchema.from_orm(todo) for todo in todos[::-1]]
        )

    return ToDoListSchema(
        todos=[ToDoSchema.from_orm(todo) for todo in todos]
    )


@app.get("/todos/{id}")
def get_todo_handler(
        id: int,
        session: Session = Depends(get_db)
) -> ToDoSchema:
    todo = get_todo_by_id(session, id)

    if todo:
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found")


@app.post("/todos", status_code=201)
def create_todo_handler(
        request: CreateToDoRequest,
        session: Session = Depends(get_db)
) -> ToDoSchema:
    todo = create_todo(session, ToDo.create(request))

    return ToDoSchema.from_orm(todo)


@app.patch("/todos/{id}")
def update_todo_handler(
        id: int,
        is_done: bool = Body(..., embed=True),
        session: Session = Depends(get_db)
):
    todo = get_todo_by_id(session, id)

    if todo:
        todo.done() if is_done else todo.undone()
        todo = update_todo(session, todo)

        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found")


@app.delete("/todos/{id}", status_code=204)
def delete_todo_handler(
        id: int,
        session: Session = Depends(get_db)
):
    todo = get_todo_by_id(session, id)

    if todo is None:
        raise HTTPException(status_code=404, detail=todo_data)

    delete_todo(session, id)
