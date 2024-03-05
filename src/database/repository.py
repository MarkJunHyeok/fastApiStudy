from typing import List

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.conection import get_db
from database.orm import ToDo, User


class ToDoRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_todos(self) -> List[ToDo]:
        return list(self.session.scalars(select(ToDo)))

    def get_todo_by_id(self, id: int) -> ToDo | None:
        return self.session.scalar(select(ToDo).where(ToDo.id == id))

    def create_todo(self, todo: ToDo):
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def update_todo(self, todo: ToDo):
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete_todo(self, todo_id: int):
        self.session.execute(delete(ToDo).where(ToDo.id == todo_id))
        self.session.commit()


class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.username == username)
        )

    def save_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user
