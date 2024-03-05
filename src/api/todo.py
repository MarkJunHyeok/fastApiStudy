from typing import List

from fastapi import Body, HTTPException, Depends, APIRouter

from database.orm import ToDo
from database.repository import ToDoRepository, UserRepository
from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema
from security.security import get_access_token
from service.user import UserService

router = APIRouter(prefix='/todos')


@router.get("", status_code=200)
def get_todos_handler(
        access_token: str = Depends(get_access_token),
        order: str | None = None,
        user_service: UserService = Depends(UserService),
        user_repo: UserRepository = Depends(UserRepository)
) -> ToDoListSchema:
    username: str = user_service.decode_jwt(access_token=access_token)

    user = user_repo.get_user_by_username(username)

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

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
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> ToDoSchema:
    todo = todo_repo.create_todo(ToDo.create(request))

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
