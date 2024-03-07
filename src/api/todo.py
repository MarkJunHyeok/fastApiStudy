from typing import List

from fastapi import Body, HTTPException, Depends, APIRouter

from api.schema.todo.todo_create_dto import CreateToDoRequest
from api.schema.todo.todo_schema import ToDoListSchema, ToDoSchema
from domain.todo import ToDo
from domain.user import User
from repository.todo import ToDoRepository
from security.security import get_authenticated_user

router = APIRouter(prefix='/todos')


@router.get("", status_code=200)
def get_todos_handler(
        user: User = Depends(get_authenticated_user),
        order: str | None = None,
) -> ToDoListSchema:
    todos: List[ToDo] = user.todos

    if order == "DESC":
        return ToDoListSchema(
            todos=[ToDoSchema.from_orm(todo) for todo in todos[::-1]]
        )

    return ToDoListSchema(
        todos=[ToDoSchema.from_orm(todo) for todo in todos]
    )


@router.get("/{id}")
def get_todo_handler(
        id: int,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> ToDoSchema:
    todo = todo_repo.get_todo_by_id(id)

    if todo:
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found")


@router.post("", status_code=201)
def create_todo_handler(
        request: CreateToDoRequest,
        todo_repo: ToDoRepository = Depends(ToDoRepository),
        user: User = Depends(get_authenticated_user),
) -> ToDoSchema:
    todo = todo_repo.create_todo(
        ToDo.create(request.contents, request.is_done, user)
    )

    return ToDoSchema.from_orm(todo)


@router.patch("/{id}")
def update_todo_handler(
        id: int,
        is_done: bool = Body(..., embed=True),
        todo_repo: ToDoRepository = Depends(ToDoRepository)
):
    todo = todo_repo.get_todo_by_id(id)

    if todo:
        todo.done() if is_done else todo.undone()
        todo = todo_repo.update_todo(todo)

        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found")


@router.delete("/{id}", status_code=204)
def delete_todo_handler(
        id: int,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
):
    todo = todo_repo.get_todo_by_id(id)

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo Not Found")

    todo_repo.delete_todo(id)
