from typing import List

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from config.conection import get_db
from domain.todo import ToDo


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
